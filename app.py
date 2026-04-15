import streamlit as st
import numpy as np
import time

# 导入你写好的 AI 和 原有环境的判断函数
from student import Search
from gomoku import check_win, is_board_full

# 定义常量
EMPTY = 0
PLAYER = 1  # 人类玩家 (黑子)
AI = 2  # AI玩家 (白子)
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

# 设置网页标题和布局
st.set_page_config(page_title="技能五子棋 AI 对战", page_icon="⚔️", layout="centered")
st.title("⚔️ 技能五子棋 Web 挑战版")

# 侧边栏：游戏规则和状态控制
with st.sidebar:
    st.header("🎮 游戏控制")
    if st.button("🔄 重新开始游戏", use_container_width=True):
        init_game()
        st.rerun()

    st.markdown("---")
    st.subheader("✨ 你的专属技能")

    # 技能按钮逻辑
    if not st.session_state.skill_used and not st.session_state.game_over:
        btn_text = "❌ 取消释放" if st.session_state.skill_mode else "🌟 释放【无中生有】"
        if st.button(btn_text, use_container_width=True):
            st.session_state.skill_mode = not st.session_state.skill_mode
    elif st.session_state.skill_used:
        st.button("🚫 技能本局已使用", disabled=True, use_container_width=True)

    st.markdown("""
    **📜 游戏规则**：
    - 你执 **黑子 (⚫)**，先手；AI 执 **白子 (⚪)**。
    - **技能**：每局限用一次，指定一个空位 (🔶)，AI 在下一回合**绝对不能**下在该位置。
    - 获胜条件：五子连珠。
    """)


# 处理玩家点击棋盘的逻辑
def handle_click(r, c):
    if st.session_state.game_over or st.session_state.current_player != PLAYER:
        return

    # 1. 如果正在释放技能
    if st.session_state.skill_mode:
        if st.session_state.board[r][c] == EMPTY:
            st.session_state.board[r][c] = SKILL_P
            st.session_state.skill_used = True
            st.session_state.skill_mode = False
        else:
            st.toast("⚠️ 技能只能释放在没有棋子的地方！", icon="⚠️")
        return

    # 2. 如果是正常落子
    if st.session_state.board[r][c] == SKILL_A:
        st.toast("❌ 此位置被 AI 的技能封锁，不能落子！", icon="🚨")
        return
    if st.session_state.board[r][c] != EMPTY and st.session_state.board[r][c] != SKILL_P:
        return  # 位置已被占用

    # 玩家落子前，清除 AI 上一回合留下的技能封锁
    st.session_state.board[st.session_state.board == SKILL_A] = EMPTY

    # 玩家落子
    st.session_state.board[r][c] = PLAYER

    # 判断玩家是否获胜
    if check_win(st.session_state.board, r, c):
        st.session_state.game_over = True
        st.session_state.winner = PLAYER
    elif is_board_full(st.session_state.board):
        st.session_state.game_over = True
        st.session_state.winner = 0
    else:
        st.session_state.current_player = AI  # 轮到 AI


# 👇 这里是全新的 CSS 魔法，修复了所有视觉问题
st.markdown("""
    <style>
    /* 1. 保护侧边栏：让侧边栏的按钮恢复正常的宽度和高度，解决文字溢出！ */
    [data-testid="stSidebar"] div.stButton > button {
        height: auto !important;
        width: 100% !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
    }

    /* 2. 改造棋盘按钮：变成直角方块，设置木板底色和网格边框 */
    [data-testid="stMainBlockContainer"] div.stButton > button {
        height: 44px;
        width: 44px;
        border-radius: 0px; /* 去除圆角，变成直角方便拼合 */
        padding: 0;
        font-size: 26px;
        background-color: #E6C280; /* 木板色 */
        border: 1px solid #8B4513; /* 深棕色网格线 */
        margin: 0;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    [data-testid="stMainBlockContainer"] div.stButton > button:hover {
        background-color: #D2B48C;
        border: 1px solid #8B4513;
        color: inherit;
    }

    /* 3. 缝合棋盘：强行消除 Streamlit 列与列之间的所有缝隙 */
    [data-testid="stHorizontalBlock"] {
        gap: 0rem !important; /* 消除左右间隙 */
        justify-content: center; /* 让整个棋盘居中 */
    }
    [data-testid="column"] {
        min-width: 0 !important;
        padding: 0 !important; /* 消除列的内边距 */
        width: 44px !important; /* 强制列宽等于按钮宽度 */
        flex: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 渲染 11x11 棋盘
for i in range(11):
    cols = st.columns(11)  # 不再使用 gap 参数，全靠 CSS 缝合
    for j in range(11):
        val = st.session_state.board[i][j]

        # 移除了"➕"符号，使用空白字符 "\u2001" (Em Quad) 撑起空位
        label = "\u2001" if val == EMPTY else "⚫" if val == PLAYER else "⚪" if val == AI else "🔶" if val == SKILL_P else "🔷"

        # 如果游戏结束或是 AI 回合，禁用按钮
        disabled = st.session_state.game_over or st.session_state.current_player != PLAYER

        with cols[j]:
            st.button(label, key=f"btn_{i}_{j}", on_click=handle_click, args=(i, j), disabled=disabled)

# 轮到 AI 思考并行动
if st.session_state.current_player == AI and not st.session_state.game_over:
    with st.spinner("🤖 AI 正在深度思考中 (可能会花几十秒)..."):
        # 调用你的 AI
        board_for_ai = st.session_state.board.copy()
        move, skill = st.session_state.ai_agent.make_move(board_for_ai)

        # AI 释放技能
        if skill is not None:
            sr, sc = skill
            st.session_state.board[sr][sc] = SKILL_A

        # AI 落子
        if move is not None:
            mr, mc = move
            if st.session_state.board[mr][mc] == SKILL_P:
                # 检查 AI 是否违规下在了玩家封锁的地方
                st.session_state.game_over = True
                st.session_state.winner = PLAYER
                st.error("🎉 AI 尝试在被封锁的位置落子，AI 违规直接判负！")
            else:
                st.session_state.board[mr][mc] = AI
                if check_win(st.session_state.board, mr, mc):
                    st.session_state.game_over = True
                    st.session_state.winner = AI
                elif is_board_full(st.session_state.board):
                    st.session_state.game_over = True
                    st.session_state.winner = 0

        # AI 落子后，清除玩家上一回合留下的技能封锁
        st.session_state.board[st.session_state.board == SKILL_P] = EMPTY

        if not st.session_state.game_over:
            st.session_state.current_player = PLAYER
            st.rerun()  # 刷新界面，交还给玩家

# 游戏结束提示
if st.session_state.game_over:
    if st.session_state.winner == PLAYER:
        st.success("🎉 恭喜！你战胜了 AI！")
        st.balloons()
    elif st.session_state.winner == AI:
        st.error("💻 AI 获胜了，再接再厉！人类的荣耀需要你来守护！")
    else:
        st.info("🤝 双方平局！棋逢对手。")