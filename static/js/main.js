document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector(".site-header");

    if (header) {
        let lastScrollY = Math.max(window.scrollY, 0);
        let scrollDirection = 0;
        let traveledDistance = 0;
        let ticking = false;

        const updateHeader = () => {
            const currentScrollY = Math.max(window.scrollY, 0);
            const delta = currentScrollY - lastScrollY;
            const nextDirection = delta > 0 ? 1 : delta < 0 ? -1 : scrollDirection;

            if (nextDirection !== scrollDirection) {
                scrollDirection = nextDirection;
                traveledDistance = 0;
            }

            traveledDistance += Math.abs(delta);

            if (currentScrollY <= 40) {
                header.classList.remove("is-hidden");
            } else if (
                scrollDirection === 1
                && currentScrollY >= 120
                && traveledDistance >= 64
                && !header.contains(document.activeElement)
            ) {
                header.classList.add("is-hidden");
                traveledDistance = 0;
            } else if (scrollDirection === -1 && traveledDistance >= 48) {
                header.classList.remove("is-hidden");
                traveledDistance = 0;
            }

            lastScrollY = currentScrollY;
            ticking = false;
        };

        window.addEventListener("scroll", () => {
            if (!ticking) {
                window.requestAnimationFrame(updateHeader);
                ticking = true;
            }
        }, { passive: true });
    }

    let navigationController = null;

    const moveIndicator = (tabList, tab) => {
        tabList.style.setProperty("--indicator-x", `${tab.offsetLeft}px`);
        tabList.style.setProperty("--indicator-width", `${tab.offsetWidth}px`);
    };

    const initializeIndicator = () => {
        const tabList = document.querySelector(".sort-tabs");
        const activeTab = tabList?.querySelector(".sort-tab.is-active");

        if (!tabList || !activeTab) {
            return;
        }

        tabList.classList.remove("is-ready");
        moveIndicator(tabList, activeTab);
        requestAnimationFrame(() => tabList.classList.add("is-ready"));
    };

    const activateSortTab = (selectedTab) => {
        const tabList = selectedTab.closest(".sort-tabs");

        if (!tabList) {
            return;
        }

        tabList.querySelectorAll(".sort-tab").forEach((tab) => {
            const isSelected = tab === selectedTab;
            tab.classList.toggle("is-active", isSelected);

            if (isSelected) {
                tab.setAttribute("aria-current", "page");
            } else {
                tab.removeAttribute("aria-current");
            }
        });

        moveIndicator(tabList, selectedTab);
    };

    const syncSortControls = (currentSortRow, nextSortRow) => {
        const currentTabs = [...currentSortRow.querySelectorAll(".sort-tab")];
        const nextTabs = [...nextSortRow.querySelectorAll(".sort-tab")];
        const nextActiveIndex = nextTabs.findIndex((tab) =>
            tab.classList.contains("is-active"),
        );

        currentTabs.forEach((tab, index) => {
            const nextTab = nextTabs[index];
            if (nextTab) {
                tab.href = nextTab.href;
            }
        });

        if (nextActiveIndex >= 0 && currentTabs[nextActiveIndex]) {
            activateSortTab(currentTabs[nextActiveIndex]);
        }

        const currentPeriodFilter = currentSortRow.querySelector(".period-filter");
        const nextPeriodFilter = nextSortRow.querySelector(".period-filter");
        if (currentPeriodFilter && nextPeriodFilter) {
            currentPeriodFilter.replaceWith(nextPeriodFilter);
        }
    };

    const replaceMainContent = async (url, shouldPushHistory = true) => {
        const currentGrid = document.querySelector(".content-grid");
        const currentSortRow = document.querySelector(".sort-row");

        if (!currentGrid || !currentSortRow) {
            window.location.assign(url);
            return;
        }

        navigationController?.abort();
        navigationController = new AbortController();
        const savedScrollY = window.scrollY;

        currentGrid.classList.add("is-updating");
        currentGrid.setAttribute("aria-busy", "true");

        try {
            const response = await fetch(url, {
                headers: { "X-Requested-With": "fetch" },
                signal: navigationController.signal,
            });

            if (!response.ok) {
                throw new Error(`페이지를 불러오지 못했습니다: ${response.status}`);
            }

            const nextDocument = new DOMParser().parseFromString(
                await response.text(),
                "text/html",
            );
            const nextGrid = nextDocument.querySelector(".content-grid");
            const nextSortRow = nextDocument.querySelector(".sort-row");

            if (!nextGrid || !nextSortRow) {
                throw new Error("교체할 콘텐츠를 찾지 못했습니다.");
            }

            nextGrid.classList.add("is-entering");
            syncSortControls(currentSortRow, nextSortRow);
            currentGrid.replaceWith(nextGrid);
            document.title = nextDocument.title;

            if (shouldPushHistory) {
                window.history.pushState({}, "", url);
            }

            window.scrollTo(0, savedScrollY);

            requestAnimationFrame(() => {
                requestAnimationFrame(() => nextGrid.classList.remove("is-entering"));
            });
        } catch (error) {
            if (error.name === "AbortError") {
                return;
            }

            window.location.assign(url);
        } finally {
            document.querySelector(".content-grid")?.removeAttribute("aria-busy");
        }
    };

    document.addEventListener("click", (event) => {
        const link = event.target.closest(".sort-tab, .period-option");

        if (
            !link
            || event.button !== 0
            || event.metaKey
            || event.ctrlKey
            || event.shiftKey
            || event.altKey
        ) {
            return;
        }

        const nextUrl = new URL(link.href, window.location.href);

        if (nextUrl.origin !== window.location.origin) {
            return;
        }

        event.preventDefault();
        link.closest("details")?.removeAttribute("open");

        if (link.classList.contains("sort-tab")) {
            activateSortTab(link);
        }

        if (nextUrl.href === window.location.href) {
            return;
        }

        replaceMainContent(nextUrl.href);
    });

    document.addEventListener("click", (event) => {
        document.querySelectorAll(".period-filter[open]").forEach((filter) => {
            if (!filter.contains(event.target)) {
                filter.removeAttribute("open");
            }
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }

        const openFilter = document.querySelector(".period-filter[open]");

        if (openFilter) {
            openFilter.removeAttribute("open");
            openFilter.querySelector("summary")?.focus();
        }
    });

    window.addEventListener("popstate", () => {
        replaceMainContent(window.location.href, false);
    });

    window.addEventListener("pageshow", (event) => {
        if (event.persisted) {
            replaceMainContent(window.location.href, false);
        }
    });

    window.addEventListener("resize", initializeIndicator);
    initializeIndicator();
});
