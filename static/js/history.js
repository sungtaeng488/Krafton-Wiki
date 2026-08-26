document.addEventListener("DOMContentLoaded", () => {
    const historyList = document.querySelector(".history-list");
    if (!historyList) {
        return;
    }

    let navigationController = null;

    const activateHistoryItem = (selectedItem) => {
        historyList.querySelectorAll(".history-item").forEach((item) => {
            const isSelected = item === selectedItem;
            item.classList.toggle("is-active", isSelected);

            if (isSelected) {
                item.setAttribute("aria-current", "page");
            } else {
                item.removeAttribute("aria-current");
            }
        });
    };

    const syncHistorySelection = (nextDocument) => {
        const nextActiveItem = nextDocument.querySelector(
            ".history-item.is-active",
        );
        const nextActiveUrl = nextActiveItem
            ? new URL(nextActiveItem.href, window.location.origin).href
            : null;
        const currentActiveItem = [...historyList.querySelectorAll(".history-item")]
            .find((item) => item.href === nextActiveUrl);

        activateHistoryItem(currentActiveItem || null);
    };

    const replaceHistoryPreview = async (url, shouldPushHistory = true) => {
        const currentPreview = document.querySelector(".history-preview");
        if (!currentPreview) {
            window.location.assign(url);
            return;
        }

        navigationController?.abort();
        const controller = new AbortController();
        navigationController = controller;
        currentPreview.classList.add("is-updating");
        currentPreview.setAttribute("aria-busy", "true");

        try {
            const response = await fetch(url, {
                headers: { "X-Requested-With": "fetch" },
                signal: controller.signal,
            });
            if (!response.ok) {
                throw new Error(`히스토리를 불러오지 못했습니다: ${response.status}`);
            }

            const nextDocument = new DOMParser().parseFromString(
                await response.text(),
                "text/html",
            );
            const nextPreview = nextDocument.querySelector(".history-preview");
            if (!nextPreview) {
                throw new Error("교체할 히스토리 내용을 찾지 못했습니다.");
            }

            nextPreview.classList.add("is-entering");
            syncHistorySelection(nextDocument);
            currentPreview.replaceWith(nextPreview);
            document.title = nextDocument.title;

            if (shouldPushHistory) {
                window.history.pushState({}, "", url);
            }

            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    nextPreview.classList.remove("is-entering");
                });
            });
        } catch (error) {
            if (error.name === "AbortError") {
                return;
            }

            window.location.assign(url);
        } finally {
            if (navigationController === controller) {
                const activePreview = document.querySelector(".history-preview");
                activePreview?.classList.remove("is-updating");
                activePreview?.removeAttribute("aria-busy");
            }
        }
    };

    historyList.addEventListener("click", (event) => {
        const link = event.target.closest(".history-item");
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
        activateHistoryItem(link);

        if (nextUrl.href === window.location.href) {
            return;
        }

        replaceHistoryPreview(nextUrl.href);
    });

    window.addEventListener("popstate", () => {
        replaceHistoryPreview(window.location.href, false);
    });
});
