document.addEventListener("DOMContentLoaded", () => {
    let refreshController = null;

    const refreshMyPage = async () => {
        const currentSummary = document.querySelector(".mypage-summary");
        const currentPosts = document.querySelector(".my-posts");

        if (!currentSummary || !currentPosts) {
            return;
        }

        refreshController?.abort();
        refreshController = new AbortController();
        currentSummary.setAttribute("aria-busy", "true");
        currentPosts.setAttribute("aria-busy", "true");

        try {
            const response = await fetch(window.location.href, {
                headers: { "X-Requested-With": "fetch" },
                signal: refreshController.signal,
            });

            if (response.redirected) {
                window.location.assign(response.url);
                return;
            }

            if (!response.ok) {
                throw new Error(`마이페이지를 불러오지 못했습니다: ${response.status}`);
            }

            const nextDocument = new DOMParser().parseFromString(
                await response.text(),
                "text/html",
            );
            const nextSummary = nextDocument.querySelector(".mypage-summary");
            const nextPosts = nextDocument.querySelector(".my-posts");

            if (!nextSummary || !nextPosts) {
                throw new Error("갱신할 마이페이지 정보를 찾지 못했습니다.");
            }

            currentSummary.replaceWith(nextSummary);
            currentPosts.replaceWith(nextPosts);
        } catch (error) {
            if (error.name !== "AbortError") {
                console.error(error);
            }
        } finally {
            document.querySelector(".mypage-summary")?.removeAttribute("aria-busy");
            document.querySelector(".my-posts")?.removeAttribute("aria-busy");
        }
    };

    window.addEventListener("pageshow", (event) => {
        if (event.persisted) {
            refreshMyPage();
        }
    });
});
