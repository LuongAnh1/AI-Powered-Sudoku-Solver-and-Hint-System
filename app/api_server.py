# app/api_server.py
import os
import sys
import time
import tempfile
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    import sudoku_solver_cpp
    print("✅ [INFO] Nạp thành công module giải Sudoku viết bằng C++!")
except ImportError as e:
    print(f"❌ [ERROR] Không thể nạp module C++: {e}")
    sys.exit(1)

from cv.detector import find_sudoku_grid, extract_cells_smart
from cv.recognizer import SudokuRecognizer

app = FastAPI(title="Sudoku Solver Web API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

onnx_path = os.path.join(current_dir, "models", "digit_model.onnx")
recognizer = SudokuRecognizer(model_path=onnx_path)

# ==========================================
# CÁC MODEL DỮ LIỆU GIAO TIẾP VỚI WEB
# ==========================================
class BoardState(BaseModel):
    matrix: list[list[int]]


# Helper hỗ trợ trích xuất thuộc tính C++ an toàn
def get_attr(obj, *names, default=None):
    for name in names:
        if hasattr(obj, name): return getattr(obj, name)
    return default


# ==========================================
# API 1: TRÍCH XUẤT ẢNH -> ĐỀ BÀI + SỐ NHÁP BAN ĐẦU
# ==========================================
@app.post("/api/extract")
async def extract_sudoku_api(file: UploadFile = File(...)):
    temp_file_path = None
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name

        warped_grid = find_sudoku_grid(temp_file_path, output_size=450)
        if warped_grid is None:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Không tìm thấy lưới Sudoku."})

        cells_9x9 = extract_cells_smart(warped_grid, output_size=450, margin=4)
        detected_matrix = recognizer.recognize_grid(cells_9x9)

        # Khởi tạo C++ để lấy số nháp (candidates) ban đầu
        engine = sudoku_solver_cpp.SolverEngine()
        engine.load_grid(detected_matrix)
        
        if hasattr(engine, "get_grid_candidates"): init_candidates = engine.get_grid_candidates()
        elif hasattr(engine, "GetGridCandidates"): init_candidates = engine.GetGridCandidates()
        else: init_candidates = []

        return {
            "status": "success", 
            "detected_grid": detected_matrix,
            "candidates": init_candidates
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# ==========================================
# API 2: GIẢI NHANH TOÀN BỘ
# ==========================================
@app.post("/api/solve")
async def solve_sudoku_api(board: BoardState):
    try:
        engine = sudoku_solver_cpp.SolverEngine()
        engine.load_grid(board.matrix)
        
        start_time = time.perf_counter()
        engine.solve_full()
        end_time = time.perf_counter()
        
        solved_matrix = engine.get_grid()
        solve_time_ms = (end_time - start_time) * 1000

        return {"status": "success", "solved_grid": solved_matrix, "solve_time_ms": round(solve_time_ms, 3)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


# ==========================================
# API 3: LẬP LỊCH TOÀN BỘ CHUỖI GỢI Ý + SỐ NHÁP TỪNG BƯỚC
# ==========================================
@app.post("/api/generate_chain")
async def generate_hint_chain_api(board: BoardState):
    try:
        engine = sudoku_solver_cpp.SolverEngine()
        engine.load_grid(board.matrix)
        
        all_hints = []
        safety_limit = 81 

        for _ in range(safety_limit):
            if hasattr(engine, "get_next_hint"): hint_cpp = engine.get_next_hint()
            elif hasattr(engine, "GetNextHint"): hint_cpp = engine.GetNextHint()
            else: break

            found = get_attr(hint_cpp, "found", "found_", default=False)
            if not found: break

            pattern_cells = []
            for p in get_attr(hint_cpp, "patternCells", "pattern_cells", default=[]):
                if hasattr(p, "__len__") and len(p) >= 2: pattern_cells.append((p[0], p[1]))
                elif hasattr(p, "row") and hasattr(p, "col"): pattern_cells.append((p.row, p.col))

            eliminations = []
            for e in get_attr(hint_cpp, "eliminations", default=[]):
                r = get_attr(e, "row", default=-1)
                c = get_attr(e, "col", default=-1)
                v = get_attr(e, "value", default=0)
                if r != -1 and c != -1: eliminations.append({"row": r, "col": c, "value": v})

            target_row = get_attr(hint_cpp, "fillRow", "fill_row", default=-1)
            target_col = get_attr(hint_cpp, "fillCol", "fill_col", default=-1)
            target_val = get_attr(hint_cpp, "fillValue", "fill_value", default=0)

            # Đồng bộ ngược vào C++ để tìm bước kế tiếp
            for elim in eliminations:
                if hasattr(engine, "remove_candidate"):
                    engine.remove_candidate(elim["row"], elim["col"], elim["value"])
            
            if target_row != -1 and target_col != -1 and target_val > 0:
                success = False
                for method in ["place_value", "PlaceValue", "set_cell", "SetCell"]:
                    if hasattr(engine, method):
                        try:
                            # ĐỒNG BỘ ĐÚNG THỨ TỰ (HÀNG - CỘT)
                            getattr(engine, method)(target_row, target_col, target_val) 
                            success = True
                            break
                        except: pass
                if not success:
                    board.matrix[target_row][target_col] = target_val
                    engine.load_grid(board.matrix)

            # Chụp lại ảnh trạng thái số nháp (candidates) sau khi áp dụng bước này
            if hasattr(engine, "get_grid_candidates"): step_candidates = engine.get_grid_candidates()
            elif hasattr(engine, "GetGridCandidates"): step_candidates = engine.GetGridCandidates()
            else: step_candidates = []

            parsed_hint = {
                "strategy_name": get_attr(hint_cpp, "strategyName", "strategy_name", default=""),
                "explanation": get_attr(hint_cpp, "explanation", default=""),
                "row": target_row,
                "col": target_col,
                "value": target_val,
                "pattern_cells": pattern_cells,
                "eliminations": eliminations,
                "candidates": step_candidates # Gửi kèm trạng thái số nháp của bước này về Web
            }
            all_hints.append(parsed_hint)

        return {"status": "success", "chain": all_hints}

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


# ==========================================
# GIAO DIỆN WEB (FRONTEND HTML/JS)
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    html_content = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI-Powered Sudoku Solver</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .sudoku-grid { display: grid; grid-template-columns: repeat(9, minmax(0, 1fr)); border: 3px solid #1e293b; background-color: #cbd5e1; gap: 1px; }
            .sudoku-cell { aspect-ratio: 1; background-color: #ffffff; cursor: pointer; transition: background-color 0.2s; }
            .sudoku-cell:nth-child(3n) { margin-right: 2px; }
            .sudoku-cell:nth-child(9n) { margin-right: 0; }
            .sudoku-grid > div:nth-child(n+19):nth-child(-n+27), .sudoku-grid > div:nth-child(n+46):nth-child(-n+54) { margin-bottom: 2px; }
        </style>
    </head>
    <body class="bg-[#0F172A] text-white font-sans min-h-screen flex flex-col">
        <main class="flex-grow w-full max-w-[1280px] mx-auto p-4 grid grid-cols-1 lg:grid-cols-[320px_1fr_380px] gap-6">
            <!-- CỘT TRÁI -->
            <div class="flex flex-col h-full">
                <div class="mb-6">
                    <h1 class="text-3xl font-bold text-white">SUDOKU <span class="text-[#38BDF8]">AI</span></h1>
                    <p class="text-xs text-[#64748B] mt-1">Logical Deduction Engine (Web)</p>
                </div>
                <div class="bg-[#1E293B] rounded-2xl border border-[#334155] flex-grow flex flex-col overflow-hidden">
                    <div class="px-5 py-4 border-b border-[#334155] flex items-center">
                        <span class="text-[#38BDF8] text-xl mr-2">✦</span>
                        <h2 class="text-lg font-bold text-[#38BDF8]">Giải thích</h2>
                    </div>
                    <div class="p-5 flex-grow">
                        <p id="explanation-box" class="text-[#E2E8F0] text-sm leading-relaxed whitespace-pre-wrap">Hệ thống sẵn sàng. Nhấp chuột vào một ô hoặc chọn 'Nạp ảnh Sudoku'.</p>
                    </div>
                </div>
            </div>

            <!-- CỘT GIỮA -->
            <div class="flex items-center justify-center p-4">
                <div class="bg-[#1E293B] p-2 rounded-2xl border-2 border-[#2563EB] w-full max-w-[500px] shadow-2xl">
                    <div id="sudoku-board" class="sudoku-grid"></div>
                </div>
            </div>

            <!-- CỘT PHẢI -->
            <div class="bg-[#1E293B] rounded-2xl border border-[#334155] flex flex-col overflow-hidden">
                <h2 class="px-5 py-4 text-sm font-bold text-[#38BDF8] tracking-wider">🖼️ ẢNH SUDOKU GỐC</h2>
                <div class="bg-[#0F172A] mx-5 mb-5 rounded-xl border border-[#334155] aspect-square flex items-center justify-center overflow-hidden relative cursor-pointer" onclick="document.getElementById('file-input').click()">
                    <input type="file" id="file-input" class="hidden" accept="image/*" onchange="uploadImage(event)">
                    <p id="preview-text" class="text-[#64748B] text-sm text-center px-4">Chưa có ảnh được nạp<br><br>Nhấp chọn nút bên dưới để tải tệp lên</p>
                    <img id="image-preview" class="hidden w-full h-full object-contain" />
                </div>
                <div class="px-5 pb-5 grid grid-cols-2 gap-3 mt-auto">
                    <button onclick="document.getElementById('file-input').click()" class="col-span-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white py-2.5 rounded-lg font-bold text-sm transition">Nạp ảnh Sudoku</button>
                    <button onclick="quickSolve()" class="bg-[#10B981] hover:bg-[#059669] text-white py-2.5 rounded-lg font-bold text-sm transition">⚡ Giải nhanh</button>
                    <button id="hint-btn" onclick="nextHint()" class="bg-[#F97316] hover:bg-[#EA580C] text-white py-2.5 rounded-lg font-bold text-sm transition">💡 Gợi ý kế tiếp</button>
                    <button onclick="resetBoard()" class="col-span-2 bg-[#EF4444] hover:bg-[#DC2626] text-white py-2.5 rounded-lg font-bold text-sm transition">🔄 Làm mới bảng</button>
                </div>
            </div>
        </main>

        <script>
            // 1. BIẾN TOÀN CỤC & KHỞI TẠO CẤU TRÚC Ô CHỒNG 2 LỚP (GIỐNG PYTHON)
            const board = document.getElementById('sudoku-board');
            let originalGrid = null; 
            let preCalculatedChain = [];
            let currentHintIndex = 0;
            let currentPendingHint = null;

            for (let r = 0; r < 9; r++) {
                for (let c = 0; c < 9; c++) {
                    const cell = document.createElement('div');
                    cell.className = 'sudoku-cell relative';
                    cell.id = `cell-${r}-${c}`;
                    cell.onclick = () => onCellClick(r, c);
                    
                    // Lớp 1: Số lớn chính thức (Mặc định trống)
                    const mainVal = document.createElement('span');
                    mainVal.className = 'main-val absolute inset-0 flex items-center justify-center pointer-events-none text-2xl transition';
                    mainVal.id = `main-${r}-${c}`;
                    cell.appendChild(mainVal);
                    
                    // Lớp 2: Lưới số nháp 3x3 (Giống pencil_frame của Python)
                    const pencilGrid = document.createElement('div');
                    pencilGrid.id = `pencil-grid-${r}-${c}`;
                    pencilGrid.className = 'pencil-grid absolute inset-0 grid grid-cols-3 grid-rows-3 p-1 text-[10px] text-slate-500 leading-none pointer-events-none';
                    for (let i = 1; i <= 9; i++) {
                        const pSpan = document.createElement('span');
                        pSpan.id = `pencil-${r}-${c}-${i}`;
                        pSpan.className = 'flex items-center justify-center';
                        pencilGrid.appendChild(pSpan);
                    }
                    cell.appendChild(pencilGrid);

                    board.appendChild(cell);
                }
            }

            function updateExplanation(text) { document.getElementById('explanation-box').innerText = text; }

            // Hàm trích xuất ma trận hiện tại từ giao diện Web
            function getHTMLMatrix() {
                let currentMatrix = [];
                for (let r = 0; r < 9; r++) {
                    let row = [];
                    for (let c = 0; c < 9; c++) {
                        let val = document.getElementById(`main-${r}-${c}`).innerText;
                        row.push(val === "" ? 0 : parseInt(val));
                    }
                    currentMatrix.push(row);
                }
                return currentMatrix;
            }

            // Hàm vẽ/đồng bộ số nháp (Pencil marks) cho một ô chỉ định
            function setCellPencilMarks(r, c, candidates) {
                const pencilGrid = document.getElementById(`pencil-grid-${r}-${c}`);
                const mainValText = document.getElementById(`main-${r}-${c}`).innerText;

                // Nếu ô đã được điền số lớn chính thức, ẩn lưới số nháp đi (Giống tkraise)
                if (mainValText !== "") {
                    pencilGrid.classList.add('hidden');
                    return;
                }

                pencilGrid.classList.remove('hidden');
                for (let i = 1; i <= 9; i++) {
                    const pSpan = document.getElementById(`pencil-${r}-${c}-${i}`);
                    if (candidates && candidates.includes(i)) {
                        pSpan.innerText = i;
                    } else {
                        pSpan.innerText = "";
                    }
                }
            }

            // 2. TƯƠNG TÁC CLICK HIGHLIGHT
            function onCellClick(row, col) {
                if (currentPendingHint !== null) {
                    currentPendingHint = null;
                    const hintBtn = document.getElementById('hint-btn');
                    hintBtn.innerHTML = "💡 Gợi ý kế tiếp";
                    hintBtn.className = "bg-[#F97316] hover:bg-[#EA580C] text-white py-2.5 rounded-lg font-bold text-sm transition";
                }

                const boxR = Math.floor(row / 3) * 3, boxC = Math.floor(col / 3) * 3;
                for (let r = 0; r < 9; r++) {
                    for (let c = 0; c < 9; c++) {
                        const cell = document.getElementById(`cell-${r}-${c}`);
                        if (r === row && c === col) cell.style.backgroundColor = '#ADCFFF';
                        else if (r === row || c === col || (Math.floor(r/3)*3 === boxR && Math.floor(c/3)*3 === boxC)) cell.style.backgroundColor = '#E5F1FF';
                        else cell.style.backgroundColor = '#FFFFFF';
                    }
                }
                updateExplanation(`Đã chọn ô ở Hàng ${row + 1}, Cột ${col + 1}.\\nMàu xanh dương hiển thị hàng, cột, khối 3x3 tương ứng.`);
            }

            // 3. LẬP LỊCH CHUỖI GỢI Ý (Có đồng bộ trạng thái số nháp)
            async function generateHintChain() {
                try {
                    const response = await fetch('/api/generate_chain', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ matrix: getHTMLMatrix() })
                    });
                    const data = await response.json();
                    if (data.status === 'success') {
                        preCalculatedChain = data.chain;
                        currentHintIndex = 0;
                    }
                } catch (e) { console.error("Lỗi lập lịch", e); }
            }

            // 4. NẠP ẢNH (Tải số nháp ban đầu cùng lúc)
            async function uploadImage(event) {
                const file = event.target.files[0];
                if (!file) return;

                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('preview-text').classList.add('hidden');
                    const img = document.getElementById('image-preview');
                    img.src = e.target.result;
                    img.classList.remove('hidden');
                }
                reader.readAsDataURL(file);

                resetBoard(); 
                updateExplanation('Đang phân tích ảnh và trích xuất số... Xin vui lòng đợi.');

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/api/extract', { method: 'POST', body: formData });
                    const data = await response.json();

                    if (data.status === 'success') {
                        originalGrid = data.detected_grid;
                        
                        // 1. Điền số lớn của đề bài
                        for (let r = 0; r < 9; r++) {
                            for (let c = 0; c < 9; c++) {
                                const mainCell = document.getElementById(`main-${r}-${c}`);
                                const val = originalGrid[r][c];
                                if (val !== 0) {
                                    mainCell.innerText = val;
                                    mainCell.className = 'main-val absolute inset-0 flex items-center justify-center pointer-events-none text-2xl text-[#1A365D] font-bold';
                                }
                            }
                        }

                        // 2. Điền số nháp ứng viên ban đầu
                        if (data.candidates && data.candidates.length > 0) {
                            for (let r = 0; r < 9; r++) {
                                for (let c = 0; c < 9; c++) {
                                    setCellPencilMarks(r, c, data.candidates[r][c]);
                                }
                            }
                        }

                        updateExplanation("Nhận dạng ảnh thành công.\\nĐang lập lịch logic giải... vui lòng đợi.");
                        await generateHintChain(); 
                        
                        updateExplanation(`Nhận dạng thành công. Đã lập lịch trước ${preCalculatedChain.length} bước logic.\\nNhấn 'Gợi ý kế tiếp' để xem.`);
                        onCellClick(0, 0); 
                    } else { updateExplanation(`❌ Thất bại: ${data.message}`); }
                } catch (error) { updateExplanation('❌ Lỗi kết nối đến máy chủ API.'); }
            }

            // 5. GIẢI NHANH
            async function quickSolve() {
                const matrix = getHTMLMatrix();
                updateExplanation('Đang tiến hành giải nhanh...');

                try {
                    const response = await fetch('/api/solve', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ matrix: matrix })
                    });
                    const data = await response.json();

                    if (data.status === 'success') {
                        for (let r = 0; r < 9; r++) {
                            for (let c = 0; c < 9; c++) {
                                const mainCell = document.getElementById(`main-${r}-${c}`);
                                const solvedVal = data.solved_grid[r][c];
                                if (solvedVal !== 0 && mainCell.innerText === "") {
                                    mainCell.innerText = solvedVal;
                                    mainCell.className = 'main-val absolute inset-0 flex items-center justify-center pointer-events-none text-2xl text-[#2563EB] font-bold'; 
                                }
                                // Ẩn toàn bộ lưới số nháp đi sau khi giải nhanh hoàn tất
                                document.getElementById(`pencil-grid-${r}-${c}`).classList.add('hidden');
                            }
                        }
                        updateExplanation(`✅ Giải thành công bằng C++ Engine trong ${data.solve_time_ms} ms!`);
                    } else {
                        updateExplanation(`❌ Thất bại: ${data.message}`);
                    }
                } catch (error) { updateExplanation('❌ Lỗi kết nối đến máy chủ API.'); }
            }

            // 6. GỢI Ý KẾ TIẾP (Đọc từ mảng, cập nhật số lớn và số nháp động)
            function nextHint() {
                const hintBtn = document.getElementById('hint-btn');

                if (currentPendingHint === null) {
                    if (preCalculatedChain.length === 0 || currentHintIndex >= preCalculatedChain.length) {
                        updateExplanation("Không còn bước giải logic nào nữa. Bàn cờ đã hoàn thành hoặc cần thuật toán quay lui.");
                        return;
                    }

                    const hint = preCalculatedChain[currentHintIndex];
                    currentPendingHint = hint;

                    // Xóa màu nền cũ
                    for (let r = 0; r < 9; r++) {
                        for (let c = 0; c < 9; c++) document.getElementById(`cell-${r}-${c}`).style.backgroundColor = '#FFFFFF';
                    }

                    // Tô màu Gợi ý (Vàng, Đỏ, Xanh lá)
                    hint.pattern_cells.forEach(([r, c]) => document.getElementById(`cell-${r}-${c}`).style.backgroundColor = '#FFE082');
                    hint.eliminations.forEach((e) => document.getElementById(`cell-${e.row}-${e.col}`).style.backgroundColor = '#FFCDD2');

                    let text = `➔ BƯỚC ${currentHintIndex + 1}/${preCalculatedChain.length}: ${hint.strategy_name}\\n${hint.explanation}`;
                    if (hint.row !== -1 && hint.value > 0) {
                        document.getElementById(`cell-${hint.row}-${hint.col}`).style.backgroundColor = '#C8E6C9';
                        text += `\\n=> ĐIỀN SỐ ${hint.value} VÀO Ô (${hint.row + 1}, ${hint.col + 1}).`;
                    }
                    updateExplanation(text);

                    hintBtn.innerHTML = "✅ Áp dụng gợi ý";
                    hintBtn.className = "bg-[#10B981] hover:bg-[#059669] text-white py-2.5 rounded-lg font-bold text-sm transition";
                } else {
                    const hint = currentPendingHint;
                    if (hint.row !== -1 && hint.value > 0) {
                        const mainCell = document.getElementById(`main-${hint.row}-${hint.col}`);
                        mainCell.innerText = hint.value;
                        mainCell.className = 'main-val absolute inset-0 flex items-center justify-center pointer-events-none text-2xl text-[#2563EB] font-bold';
                        updateExplanation(`Đã điền thành công số ${hint.value} vào ô (${hint.row + 1}, ${hint.col + 1}).\\nNhấn 'Gợi ý kế tiếp' để tiếp tục.`);
                    } else {
                        updateExplanation(`Đã loại bỏ các số nháp theo thuật toán ${hint.strategy_name}.\\nNhấn 'Gợi ý kế tiếp' để tiếp tục.`);
                    }

                    // ĐỒNG BỘ CẬP NHẬT LẠI TOÀN BỘ SỐ NHÁP TỪ C++ CHO BƯỚC NÀY
                    if (hint.candidates && hint.candidates.length > 0) {
                        for (let r = 0; r < 9; r++) {
                            for (let c = 0; c < 9; c++) {
                                setCellPencilMarks(r, c, hint.candidates[r][c]);
                            }
                        }
                    }

                    for (let r = 0; r < 9; r++) {
                        for (let c = 0; c < 9; c++) document.getElementById(`cell-${r}-${c}`).style.backgroundColor = '#FFFFFF';
                    }

                    currentPendingHint = null;
                    currentHintIndex++; // Sang bước kế tiếp
                    
                    hintBtn.innerHTML = "💡 Gợi ý kế tiếp";
                    hintBtn.className = "bg-[#F97316] hover:bg-[#EA580C] text-white py-2.5 rounded-lg font-bold text-sm transition";
                }
            }

            // 7. LÀM MỚI BẢNG
            function resetBoard() {
                for (let r = 0; r < 9; r++) {
                    for (let c = 0; c < 9; c++) {
                        const cell = document.getElementById(`cell-${r}-${c}`);
                        cell.style.backgroundColor = '#FFFFFF';
                        
                        document.getElementById(`main-${r}-${c}`).innerText = '';
                        document.getElementById(`pencil-grid-${r}-${c}`).classList.remove('hidden');
                        
                        for (let i = 1; i <= 9; i++) {
                            document.getElementById(`pencil-${r}-${c}-${i}`).innerText = '';
                        }
                    }
                }
                document.getElementById('file-input').value = '';
                document.getElementById('image-preview').classList.add('hidden');
                document.getElementById('preview-text').classList.remove('hidden');
                updateExplanation("Đã làm sạch bảng. Hệ thống sẵn sàng.");
                
                // Reset toàn bộ chuỗi gợi ý
                preCalculatedChain = [];
                currentHintIndex = 0;
                currentPendingHint = null;
                const hintBtn = document.getElementById('hint-btn');
                hintBtn.innerHTML = "💡 Gợi ý kế tiếp";
                hintBtn.className = "bg-[#F97316] hover:bg-[#EA580C] text-white py-2.5 rounded-lg font-bold text-sm transition";
            }

            window.onload = () => onCellClick(0, 0);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)