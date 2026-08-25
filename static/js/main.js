document.addEventListener("DOMContentLoaded", () => {
    const tabList = document.querySelector(".sort-tabs");
    const tabs = [...document.querySelectorAll(".sort-tab")];
    const cardGrid = document.querySelector(".content-grid");
    const cards = [...document.querySelectorAll(".card")];

    if (!tabList || tabs.length === 0) {
        return;
    }

    const moveIndicator = (tab) => {
        tabList.style.setProperty("--indicator-x", `${tab.offsetLeft}px`);
        tabList.style.setProperty("--indicator-width", `${tab.offsetWidth}px`);
    };

    const selectTab = (selectedTab) => {
        tabs.forEach((tab) => {
            const isSelected = tab === selectedTab;
            tab.classList.toggle("is-active", isSelected);
            tab.setAttribute("aria-pressed", String(isSelected));
        });

        moveIndicator(selectedTab);
    };

    const sortCards = (sortType) => {
        if (!cardGrid) {
            return;
        }

        const sortedCards = [...cards].sort((a, b) => {
            if (sortType === "likes") {
                return Number(b.dataset.likes) - Number(a.dataset.likes);
            }

            if (sortType === "latest") {
                return new Date(b.dataset.date) - new Date(a.dataset.date);
            }

            if (sortType === "views") {
                return Number(b.dataset.views) - Number(a.dataset.views);
            }

            const scoreA = Number(a.dataset.views24h) + Number(a.dataset.likes) * 3;
            const scoreB = Number(b.dataset.views24h) + Number(b.dataset.likes) * 3;
            return scoreB - scoreA;
        });

        sortedCards.forEach((card) => cardGrid.append(card));
    };

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            selectTab(tab);
            sortCards(tab.dataset.sort);
        });
    });

    const activeTab = tabs.find((tab) => tab.classList.contains("is-active")) || tabs[0];
    moveIndicator(activeTab);
    requestAnimationFrame(() => tabList.classList.add("is-ready"));

    window.addEventListener("resize", () => {
        const selectedTab = tabs.find((tab) => tab.classList.contains("is-active"));
        if (selectedTab) {
            moveIndicator(selectedTab);
        }
    });
});
