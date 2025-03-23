function toggleLike(postId) {
    fetch(`/posts/${postId}/like/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/json",
        },
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById(`like-btn-${postId}`).innerText = data.liked ? "Unlike" : "Like";
        document.getElementById(`like-count-${postId}`).innerText = data.total_likes;
    });
}

function toggleSave(postId) {
    fetch(`/posts/${postId}/save/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/json",
        },
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById(`save-btn-${postId}`).innerText = data.saved ? "Unsave" : "Save";
        document.getElementById(`save-count-${postId}`).innerText = data.total_saves;
    });
}

function addComment(postId) {
    const commentInput = document.getElementById(`comment-input-${postId}`).value;
    if (commentInput.trim() === "") return;

    fetch(`/posts/${postId}/comment/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: commentInput }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById(`comment-count-${postId}`).innerText = data.total_comments;
        document.getElementById(`comment-input-${postId}`).value = "";
    });
}

function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
}
