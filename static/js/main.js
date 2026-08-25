document.addEventListener("DOMContentLoaded", () => {
    const tabList = document.querySelector(".sort-tabs");
    const tabs = [...document.querySelectorAll(".sort-tab")];

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

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => selectTab(tab));
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
