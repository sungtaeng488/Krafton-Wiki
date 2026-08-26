const commentList = document.querySelector(".comment-list");

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

        const data = await response.json().catch(() => ({}));
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
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({text: editedText}),
                });
                if (data) {
                    commentItem.querySelector(".comment-text").textContent = data.text;
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
                    button.textContent = `♥ 좋아요 ${data.likes}`;
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
