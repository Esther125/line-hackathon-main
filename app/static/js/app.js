const fetchAboutCony = async (container) => {
    if (!container) return;
    try {
        const res = await fetch('/about-cony');
        container.innerHTML = await res.text();
    } catch (error) {
        container.innerHTML = '<p>無法載入資訊，稍後再試。</p>';
    }
};

const renderCoupons = (container, coupons) => {
    if (!container) return;
    if (!coupons.length) {
        container.innerHTML = '<li>尚無優惠券，再玩一次試試吧！</li>';
        return;
    }
    container.innerHTML = coupons
        .map(
            (coupon) => `
            <li class="coupon-card">
                <h3>${coupon.title}</h3>
                <p>${coupon.description}</p>
                <small>代碼：${coupon.id}</small>
            </li>`
        )
        .join('');
};

const fetchCoupons = async (container) => {
    if (!container) return;
    try {
        const res = await fetch('/coupons');
        const data = await res.json();
        renderCoupons(container, data.coupons || []);
    } catch (error) {
        container.innerHTML = '<li>無法取得優惠券。</li>';
    }
};

const appendChatBubble = (log, sender, text) => {
    if (!log) return;
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.textContent = text;
    log.appendChild(bubble);
    log.scrollTop = log.scrollHeight;
};

const sendChat = async (message, log) => {
    appendChatBubble(log, 'user', message);
    try {
        const res = await fetch('/chat-with-cony', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        if (!res.ok) {
            throw new Error('network');
        }
        const data = await res.json();
        appendChatBubble(log, 'cony', data.reply || 'Cony 正忙碌中，稍後回覆。');
    } catch (error) {
        appendChatBubble(log, 'cony', '糟糕，粉紅訊號斷線了，再試一次好嗎？');
    }
};

const initAboutPage = () => {
    const aboutContent = document.getElementById('about-content');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatLog = document.getElementById('chat-log');
    if (!chatForm || !chatInput || !chatLog) return;

    fetchAboutCony(aboutContent);

    chatForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;
        chatInput.value = '';
        sendChat(message, chatLog);
    });
};

const toggleGameButtons = (container, disabled) => {
    if (!container) return;
    container.querySelectorAll('button').forEach((btn) => {
        btn.disabled = disabled;
    });
};

const renderRecentCoupon = (container, coupon) => {
    if (!container) return;
    if (!coupon) {
        container.innerHTML = '<li>尚未贏得優惠券，趕快挑戰吧！</li>';
        return;
    }
    container.innerHTML = `
        <li class="coupon-card">
            <h3>${coupon.title}</h3>
            <p>${coupon.description}</p>
            <small>代碼：${coupon.id}</small>
        </li>
    `;
};

const initPlayPage = () => {
    const gameChoiceContainer = document.getElementById('game-choices');
    const gameResult = document.getElementById('game-result');
    const playCouponList = document.getElementById('play-coupon-list');
    if (!gameChoiceContainer || !gameResult) return;

    renderRecentCoupon(playCouponList, null);

    gameChoiceContainer.addEventListener('click', (event) => {
        const button = event.target.closest('button[data-choice]');
        if (!button) return;
        playGame(button.dataset.choice, gameChoiceContainer, gameResult, playCouponList);
    });
};

const playGame = async (choice, container, resultEl, recentCouponList) => {
    toggleGameButtons(container, true);
    resultEl.textContent = 'Cony 正在思考要吃什麼...';
    try {
        const res = await fetch('/play-with-cony', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_choice: choice })
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || '遊戲錯誤');
        }
        const rewardCoupon = data.reward && data.reward.new_coupon;
        const couponName = rewardCoupon && rewardCoupon.title ? rewardCoupon.title : '粉紅禮物';
        const message = data.did_win
            ? `你選了 ${choice}，Cony 也選了 ${data.cony_choice}！新增優惠券：${couponName}！`
            : `你選了 ${choice}，但Cony今天想要 ${data.cony_choice}，再接再厲！`;
        resultEl.textContent = message;
        if (data.did_win) {
            if (recentCouponList) {
                renderRecentCoupon(recentCouponList, rewardCoupon);
            }
            const globalCouponList = document.getElementById('coupon-list');
            if (globalCouponList && globalCouponList !== recentCouponList) {
                fetchCoupons(globalCouponList);
            }
        }
    } catch (error) {
        resultEl.textContent = '遊戲出錯了，請稍後再玩。';
    } finally {
        toggleGameButtons(container, false);
    }
};

const initCouponsPage = () => {
    const couponList = document.getElementById('coupon-list');
    fetchCoupons(couponList);
};

const initPage = () => {
    const pageId = document.body.dataset.page || 'home';
    if (pageId === 'about') {
        initAboutPage();
    } else if (pageId === 'play') {
        initPlayPage();
    } else if (pageId === 'coupons') {
        initCouponsPage();
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPage);
} else {
    initPage();
}
