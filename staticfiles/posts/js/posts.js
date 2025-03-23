console.log("posts.js loaded!");

function toggleLike(postId) {
    $.ajax({
        url: `/${postId}/like/`,
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() },
        success: function (data) {
            $("#like-btn-" + postId).text(data.liked ? "Unlike" : "Like");
            $("#like-count-" + postId).text(data.total_likes);
        },
        error: function () {
            alert("Error liking post.");
        }
    });
}

function toggleSave(postId) {
    $.ajax({
        url: `/${postId}/save/`,
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() },
        success: function (data) {
            $("#save-btn-" + postId).text(data.saved ? "Unsave" : "Save");
            $("#save-count-" + postId).text(data.total_saves);
        },
        error: function () {
            alert("Error saving post.");
        }
    });
}

function addComment(postId) {
    let content = $("#comment-input-" + postId).val().trim();
    if (!content) return alert("Comment cannot be empty.");

    $.ajax({
        url: `/${postId}/comment/`,
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() },
        data: { content: content },
        success: function (data) {
            $("#comment-count-" + postId).text(data.total_comments);
            $("#comment-input-" + postId).val("");
        },
        error: function () {
            alert("Error adding comment.");
        }
    });
}
