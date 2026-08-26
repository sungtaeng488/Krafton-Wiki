const commentList = document.querySelector(".comment-list");
const commentForm = document.querySelector(".comment-form");
const parseJson = (response) => response.json().catch(() => ({}));

if (commentList) {
    const postId = commentList.dataset.postId;
    const loginUrl = commentList.dataset.loginUrl;
    const isLoggedIn = commentList.dataset.isLoggedIn === "true";

    const requestComment = async (commentId, suffix, options) => {
        const response = await fetch(
            `/post/${encodeURIComponent(postId)}/comments/${encodeURIComponent(commentId)}${suffix}`,
            options,
        );

        if (response.redirected && response.url.includes("/login")) {
            window.location.href = loginUrl;
            return null;
        }

        const data = await parseJson(response);
        if (!response.ok) {
            throw new Error(data.error || "요청을 처리하지 못했습니다.");
        }

        return data;
    };

    const updateCommentCounts = (count) => {
        document.querySelectorAll("[data-comment-count]").forEach((element) => {
            element.textContent = String(count);
        });
    };

    const createCommentElement = (comment) => {
        const commentItem = document.createElement("article");
        const header = document.createElement("header");
        const author = document.createElement("strong");
        const createdAt = document.createElement("time");
        const text = document.createElement("p");
        const actions = document.createElement("div");

        commentItem.className = "comment-item";
        commentItem.dataset.commentId = comment.id;
        author.textContent = comment.author;
        createdAt.textContent = comment.created_at_text;
        text.className = "comment-text";
        text.textContent = comment.text;
        actions.className = "comment-actions";
        actions.setAttribute("aria-label", "댓글 기능");
        actions.innerHTML = `
            <button class="comment-action comment-like" type="button" data-comment-action="like">
                <span class="comment-like-heart" aria-hidden="true">♡</span>
                <span>좋아요</span>
                <span class="comment-like-count">0</span>
            </button>
            <button class="comment-action replace-comment" type="button" data-comment-action="edit">수정</button>
            <button class="comment-action delete-comment" type="button" data-comment-action="delete">삭제</button>
        `;

        header.append(author, createdAt);
        commentItem.append(header, text, actions);
        return commentItem;
    };

    if (commentForm) {
        const textarea = commentForm.querySelector("textarea[name='text']");
        const lengthElement = commentForm.querySelector("[data-comment-length]");
        const submitButton = commentForm.querySelector("button[type='submit']");
        const defaultButtonText = submitButton.textContent;
        const updateLength = () => {
            lengthElement.textContent = String(Array.from(textarea.value).length);
        };

        textarea.addEventListener("input", updateLength);
        updateLength();

        commentForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const commentText = textarea.value.trim();
            if (!commentText) {
                window.alert("댓글 내용을 입력해주세요.");
                textarea.focus();
                return;
            }
            if (Array.from(commentText).length > 1000) {
                window.alert("댓글은 최대 1,000자까지 작성할 수 있습니다.");
                textarea.focus();
                return;
            }

            submitButton.disabled = true;
            submitButton.textContent = "등록 중";

            try {
                const response = await fetch(commentForm.action, {
                    method: "POST",
                    headers: { "Accept": "application/json" },
                    body: new FormData(commentForm),
                });

                if (response.redirected && response.url.includes("/login")) {
                    window.location.href = loginUrl;
                    return;
                }

                const data = await parseJson(response);
                if (!response.ok) {
                    throw new Error(data.error || "댓글을 등록하지 못했습니다.");
                }

                commentList.querySelector(".empty-comments")?.remove();
                commentList.prepend(createCommentElement(data.comment));
                updateCommentCounts(data.comment_count);
                commentForm.reset();
                updateLength();
                textarea.focus();
            } catch (error) {
                window.alert(error.message);
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = defaultButtonText;
            }
        });
    }

    const closeEditMode = (commentItem) => {
        commentItem.querySelector(".comment-editor")?.remove();
        commentItem.querySelector(".comment-text").hidden = false;
        commentItem.querySelector(".comment-actions").hidden = false;
        commentItem.classList.remove("is-editing");
    };

    const openEditMode = (commentItem) => {
        if (commentItem.classList.contains("is-editing")) {
            return;
        }

        const textElement = commentItem.querySelector(".comment-text");
        const actions = commentItem.querySelector(".comment-actions");
        const editor = document.createElement("div");
        const textarea = document.createElement("textarea");
        const editorActions = document.createElement("div");
        const cancelButton = document.createElement("button");
        const saveButton = document.createElement("button");

        editor.className = "comment-editor";
        textarea.className = "comment-edit-textarea";
        textarea.value = textElement.textContent.trim();
        textarea.rows = 4;
        textarea.maxLength = 1000;
        textarea.setAttribute("aria-label", "댓글 내용 수정");

        editorActions.className = "comment-editor-actions";
        cancelButton.className = "comment-action comment-edit-cancel";
        cancelButton.type = "button";
        cancelButton.dataset.commentAction = "edit-cancel";
        cancelButton.textContent = "취소";

        saveButton.className = "comment-action comment-edit-save";
        saveButton.type = "button";
        saveButton.dataset.commentAction = "edit-save";
        saveButton.textContent = "저장";

        editorActions.append(cancelButton, saveButton);
        editor.append(textarea, editorActions);
        textElement.hidden = true;
        actions.hidden = true;
        commentItem.classList.add("is-editing");
        commentItem.append(editor);

        textarea.focus();
        textarea.setSelectionRange(textarea.value.length, textarea.value.length);
    };

    commentList.addEventListener("click", async (event) => {
        const button = event.target.closest("[data-comment-action]");
        if (!button) {
            return;
        }

        if (!isLoggedIn) {
            window.location.href = loginUrl;
            return;
        }

        const commentItem = button.closest(".comment-item");
        const commentId = commentItem?.dataset.commentId;
        const action = button.dataset.commentAction;
        if (!commentItem || !commentId) {
            return;
        }

        if (action === "edit") {
            openEditMode(commentItem);
            return;
        }

        if (action === "edit-cancel") {
            closeEditMode(commentItem);
            return;
        }

        if (action === "edit-save") {
            const textarea = commentItem.querySelector(".comment-edit-textarea");
            const editedText = textarea.value.trim();
            if (!editedText) {
                window.alert("댓글 내용을 입력해주세요.");
                textarea.focus();
                return;
            }

            const editorButtons = commentItem.querySelectorAll(".comment-editor button");
            editorButtons.forEach((editorButton) => {
                editorButton.disabled = true;
            });

            try {
                const data = await requestComment(commentId, "", {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({text: editedText}),
                });
                if (data) {
                    commentItem.querySelector(".comment-text").textContent = data.text;
                    let timeElement = commentItem.querySelector("time");
                    if (!timeElement) {
                        timeElement = document.createElement("time");
                        commentItem.querySelector("header").append(timeElement);
                    }
                    timeElement.textContent = data.updated_at_text;
                    closeEditMode(commentItem);
                }
            } catch (error) {
                window.alert(error.message);
                editorButtons.forEach((editorButton) => {
                    editorButton.disabled = false;
                });
            }
            return;
        }

        button.disabled = true;

        try {
            if (action === "like") {
                const data = await requestComment(commentId, "/like", {
                    method: "POST",
                });
                if (data) {
                    button.classList.toggle("is-liked", data.is_liked);
                    const heart = button.querySelector(".comment-like-heart");
                    heart.classList.toggle("is-liked", data.is_liked);
                    heart.textContent = data.is_liked ? "❤️" : "♡";
                    button.querySelector(".comment-like-count").textContent = String(data.likes);
                }
            }

            if (action === "delete") {
                const shouldDelete = window.confirm("이 댓글을 삭제할까요?");
                if (!shouldDelete) {
                    return;
                }

                const data = await requestComment(commentId, "", {
                    method: "DELETE",
                });
                if (data) {
                    commentItem.remove();
                    updateCommentCounts(data.comment_count);

                    if (!commentList.querySelector(".comment-item")) {
                        const emptyMessage = document.createElement("p");
                        emptyMessage.className = "empty-comments";
                        emptyMessage.textContent = "아직 댓글이 없습니다. 첫 댓글을 남겨보세요.";
                        commentList.append(emptyMessage);
                    }
                }
            }
        } catch (error) {
            window.alert(error.message);
        } finally {
            button.disabled = false;
        }
    });

    commentList.addEventListener("keydown", (event) => {
        const textarea = event.target.closest(".comment-edit-textarea");
        if (!textarea) {
            return;
        }

        const commentItem = textarea.closest(".comment-item");
        if (event.key === "Escape") {
            closeEditMode(commentItem);
        }

        if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
            event.preventDefault();
            commentItem.querySelector('[data-comment-action="edit-save"]').click();
        }
    });
}

const postLikeButton = document.querySelector("[data-post-like]");

if (postLikeButton) {
    postLikeButton.addEventListener("click", async () => {
        postLikeButton.disabled = true;
        postLikeButton.classList.add("is-updating");

        try {
            const response = await fetch(postLikeButton.dataset.likeUrl, {
                method: "POST",
                headers: { "Accept": "application/json" },
            });

            if (response.redirected && response.url.includes("/login")) {
                window.location.href = commentList.dataset.loginUrl;
                return;
            }

            const data = await parseJson(response);
            if (!response.ok) {
                throw new Error(data.error || "좋아요를 처리하지 못했습니다.");
            }

            postLikeButton.classList.toggle("is-liked", data.is_liked);
            const heart = postLikeButton.querySelector("[data-post-like-heart]");
            heart.classList.toggle("is-liked", data.is_liked);
            heart.textContent = data.is_liked ? "❤️" : "♡";
            document.querySelectorAll("[data-post-like-count]").forEach((element) => {
                element.textContent = String(data.likes);
            });
        } catch (error) {
            window.alert(error.message);
        } finally {
            postLikeButton.disabled = false;
            postLikeButton.classList.remove("is-updating");
        }
    });
}

const postDislikeButton = document.querySelector("[data-post-dislike]");

if (postDislikeButton) {
    postDislikeButton.addEventListener("click", async () => {
        postDislikeButton.disabled = true;
        postDislikeButton.classList.add("is-updating");

        try {
            const response = await fetch(postDislikeButton.dataset.dislikeUrl, {
                method: "POST",
                headers: { "Accept": "application/json" },
            });

            if (response.redirected && response.url.includes("/login")) {
                window.location.href = commentList.dataset.loginUrl;
                return;
            }

            const data = await parseJson(response);
            if (!response.ok) {
                throw new Error(data.error || "싫어요를 처리하지 못했습니다.");
            }

            const heart = postDislikeButton.querySelector("[data-post-dislike-heart]");
            heart.textContent = data.is_disliked ? "👎" : "✖";
            document.querySelectorAll("[data-post-dislike-count]").forEach((element) => {
                element.textContent = String(data.dislikes);
            });
        } catch (error) {
            window.alert(error.message);
        } finally {
            postDislikeButton.disabled = false;
            postDislikeButton.classList.remove("is-updating");
        }
    });
}

const deletePostForm = document.querySelector(".delete-post-form");

if (deletePostForm) {
    deletePostForm.addEventListener("submit", (event) => {
        const shouldDelete = window.confirm(
            "이 글을 삭제할까요? 삭제한 글은 되돌릴 수 없습니다.",
        );
        if (!shouldDelete) {
            event.preventDefault();
        }
    });
}
