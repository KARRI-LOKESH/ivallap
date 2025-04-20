document.addEventListener("DOMContentLoaded", () => {
    const csrfToken = getCSRFToken();

    // Handle Like button click
    document.querySelectorAll(".like-btn").forEach(button => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            const postId = button.dataset.postId;
            likePost(postId);
        });
    });

    // Handle Double-click for desktop and double-tap for mobile
    document.querySelectorAll(".post").forEach(post => {
        let lastTap = 0;
        let timeout;
        const postId = post.dataset.postId;

        post.addEventListener("dblclick", (event) => {
            if (!isInteractiveElement(event.target)) {
                likePost(postId);
            }
        });

        post.addEventListener("touchend", (event) => {
            if (!isInteractiveElement(event.target)) {
                const currentTime = new Date().getTime();
                const tapLength = currentTime - lastTap;

                if (tapLength < 100 && tapLength > 0) {
                    clearTimeout(timeout);
                    likePost(postId);
                    lastTap = 0;
                } else {
                    lastTap = currentTime;
                    timeout = setTimeout(() => {
                        lastTap = 0;
                    }, 200);
                }
            }
        });
    });

    // Like Post Function
    function likePost(postId) {
        fetch(`/posts/like/${postId}/`, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            credentials: "same-origin",
        })
        .then(response => response.json())
        .then(data => {
            const likeCount = document.getElementById(`like-count-${postId}`);
            if (likeCount) likeCount.textContent = data.total_likes;

            const likeBtn = document.querySelector(`.like-btn[data-post-id="${postId}"]`);
            if (likeBtn) likeBtn.innerHTML = data.liked ? "❤️" : "🤍";
        })
        .catch(error => console.error("Like error:", error));
    }

    // Handle Save button click
    document.querySelectorAll(".save-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();
            const postId = this.dataset.postId;
            savePost(postId);
        });
    });

    // Save Post Function
    function savePost(postId) {
        fetch(`/posts/save/${postId}/`, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            credentials: "same-origin",
        })
        .then(response => response.json())
        .then(data => {
            const saveCount = document.getElementById(`save-count-${postId}`);
            if (saveCount) saveCount.textContent = data.total_saves;

            const saveBtn = document.querySelector(`.save-btn[data-post-id="${postId}"] i`);
            if (saveBtn) {
                saveBtn.className = data.saved ? "fa fa-bookmark" : "fa fa-bookmark-o";
            }
        })
        .catch(error => console.error("Save error:", error));
    }

    // Helper function to check interactive elements
    function isInteractiveElement(el) {
        return el.closest("button, a, input, textarea") !== null;
    }

    // Helper function to get CSRF token from cookies
    function getCSRFToken() {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) {
                return cookie.substring("csrftoken=".length);
            }
        }
        return null;
    }
});
