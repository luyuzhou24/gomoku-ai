import streamlit as st
import numpy as np

# 导入你写好的 AI 和 原有环境的判断函数
from student import Search
from gomoku import check_win, is_board_full

# 定义常量
EMPTY = 0
PLAYER = 1   # 人类玩家 (黑子)
AI = 2       # AI玩家 (白子)
SKILL_P = 3  # 人类的技能封锁标记
SKILL_A = 4  # AI的技能封锁标记

# 初始化游戏状态
def init_game():
    st.session_state.board = np.zeros((11, 11), dtype=int)
    st.session_state.current_player = PLAYER
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.skill_used = False
    st.session_state.skill_mode = False
    st.session_state.ai_agent = Search(AI)

if 'board' not in st.session_state:
    init_game()

st.set_page_config(page_title="自适应技能五子棋", page_icon="⚔️", layout="centered")

# --- 响应式 CSS 优化 ---
st.markdown("""
    <style>
    /* 1. 基础尺寸变量：手机端占 90% 宽度，PC端最大 500px */
    :root {
        --board-w: min(90vw, 500px);
        --cell-size: calc(var(--board-w) / 11);
    }

    /* 2. 修复侧边栏文字溢出 */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] button {
        height: auto !important;
        width: 100% !important;
        white-space: normal !important; /* 允许文字换行 */
        padding: 10px !important;
        border-radius: 8px !important;
    }

    /* 3. 强制棋盘列不堆叠（关键：解决手机变竖列问题） */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important; /* 严禁换行 */
        gap: 0 !important;
        width: var(--board-w) !important;
        margin: 0 auto !important; /* 居中 */
    }
    
    [data-testid="column"] {
        width: var(--cell-size) !important;
        flex: 0 0 var(--cell-size) !important;
        min-width: 0 !important;
        padding: 0 !important;
    }

    /* 4. 棋盘格子样式：正方形 + 响应式大小 */
    [data-testid="stMain"] [data-testid="stVerticalBlock"] div:has(> button) button {
        width: var(--cell-size) !important;
        height: var(--cell-size) !important;
        min-width: var(--cell-size) !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 0px !important;
        border: 0.2px solid #8B4513 !important;
        background-color: #E6C280 !important;
        font-size: calc(var(--cell-size) * 0.7) !important; /* 图标随格子缩放 */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
    }

    /* 5. 隐藏 Streamlit 默认的一些间距 */
    [data-testid="stMainBlockContainer"] {
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚔️ 技能五子棋 Web")

# 侧边栏
with st.sidebar:
    st.header("🎮 控制台")
    if st.button("🔄 重新开始游戏"):
        init_game()
        st.rerun()
    
    st.markdown("---")
    if not st.session_state.skill_used and not st.session_state.game_over:
        if st.button("🌟 释放【无中生有】" if not st.session_state.skill_mode else "❌ 取消释放"):
            st.session_state.skill_mode = not st.session_state.skill_mode
    elif st.session_state.skill_used:
        st.button("🚫 技能已使用", disabled=True)

# 点击逻辑
def handle_click(r, c):
    if st.session_state.game_over or st.session_state.current_player != PLAYER:
        return
    if st.session_state.skill_mode:
        if st.session_state.board[r][c] == EMPTY:
            st.session_state.board[r][c] = SKILL_P
            st.session_state.skill_used = True
            st.session_state.skill_mode = False
        return
    if st.session_state.board[r][c] in [SKILL_A, PLAYER, AI]:
        return
    
    st.session_state.board[st.session_state.board == SKILL_A] = EMPTY
    st.session_state.board[r][c] = PLAYER
    if check_win(st.session_state.board, r, c):
        st.session_state.game_over = True
        st.session_state.winner = PLAYER
    elif is_board_full(st.session_state.board):
        st.session_state.game_over = True
        st.session_state.winner = 0
    else:
        st.session_state.current_player = AI

# 渲染棋盘
board_container = st.container()
with board_container:
    for i in range(11):
        cols = st.columns(11)
        for j in range(11):
            val = st.session_state.board[i][j]
            label = "" # 默认全空，去掉加号
            if val == PLAYER: label = "⚫"
            elif val == AI: label = "⚪"
            elif val == SKILL_P: label = "🔶"
            elif val == SKILL_A: label = "🔷"
            
            with cols[j]:
                st.button(label, key=f"b_{i}_{j}", on_click=handle_click, args=(i, j), 
                          disabled=st.session_state.game_over or st.session_state.current_player != PLAYER)

# AI 逻辑
if st.session_state.current_player == AI and not st.session_state.game_over:
    with st.status("🤖 AI 正在思考..."):
        move, skill = st.session_state.ai_agent.make_move(st.session_state.board.copy())
        if skill: st.session_state.board[skill[0]][skill[1]] = SKILL_A
        if move:
            st.session_state.board[move[0]][move[1]] = AI
            if check_win(st.session_state.board, move[0], move[1]):
                st.session_state.game_over = True
                st.session_state.winner = AI
        st.session_state.board[st.session_state.board == SKILL_P] = EMPTY
        st.session_state.current_player = PLAYER
        st.rerun()

if st.session_state.game_over:
    if st.session_state.winner == PLAYER: st.success("🎉 你赢了！")
    elif st.session_state.winner == AI: st.error("💀 AI 赢了！")
    else: st.info("🤝 平局")
