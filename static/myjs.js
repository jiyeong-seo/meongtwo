function post() {
    let comment = $("#textarea-post").val();
    let today = new Date().toISOString();
    // 강아지 사진 보내기
    let file = $("#input-pic")[0].files[0];
    let form_data = new FormData();
    form_data.append("comment_give", comment);
    form_data.append("date_give", today);
    form_data.append("img_file_give", file);
    console.log(comment, today, file, form_data);

    $.ajax({
        type: "POST",
        url: "/posting",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            $("#modal-post").removeClass("is-active");
            window.location.reload();
        },
    });
}

function commentPost(index, id) {
    let comment = $(`#comment-post${index}`).val();
    console.log("comment-post ==>", comment);
    let today = new Date().toISOString();
    let form_data = new FormData();
    form_data.append("comment_give", comment);
    form_data.append("date_give", today);
    form_data.append("id_give", id);

    console.log(comment, today, form_data, id);
    console.log("id ===>", typeof id);
    $.ajax({
        type: "POST",
        url: "/posting/comment",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            console.log("response ===>", response);
            window.location.reload()
        },
    });
}

function get_posts(username, page) {
    if (username === undefined) {
        username = "";
    }
    if (page === undefined) {
        page = 1;
    }

    $("#post-box").empty();
    $.ajax({
        type: "GET",
        url: `/get_posts?username_give=${username}&page=${page}`,
        data: {},
        success: function (response) {
            if (response["result"] === "success") {
                let posts = response["posts"];
                let comments = response.comments;
                let likes_test = response.likes;


                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i];
                    let time_post = new Date(post["date"]);
                    let time_before = time2str(time_post);
                    let class_heart = post["heart_by_me"] ? "fa-heart" : "fa-heart-o";
                    let comment_temp = ``;
                    let commentCounts = 0;

                    let likes_temp = '';
                    for (let z = 0; z < likes_test.length; z++) {

                        if (likes_test[z]['post_id'] === post._id) {


                            let likes_user = likes_test[z]['username'];
                            console.log(likes_test[z]);


                            likes_temp+=`<span class="comment-like-user">${likes_user}님 </span>`;



                        }


                    }

                    likes_temp=likes_temp+likes_test;



                    for (let j = 0; j < comments.length; j++) {
                        let comment = comments[j];
                        let time_comment = new Date(comment["date"]);
                        let time_before = time2str(time_comment);


                        if (post._id === comment.post_id) {
                            commentCounts += 1;

                            comment_temp += `
                         <div class="content comment-area__content">
                              <img class="comment-area__profile-image" src="/static/${comment.profile_pic_real}" alt="profile image">
                              <h2 class="comment-area__user-name">${comment.profile_name}</h2>
                              <p class="comment-area__comment">${comment.comment}</p>
                              <dl>
                              <dt class="sr-only">date</dt>
                              <dd class="comment-area__date">${time_before}</dd>
                              </dl>
                          </div>
                      `;
                        }
                    }

                    // 포스팅 사진
                    let html_temp = ``;
                    let postfile_pic_real = "";
                    if (!post["postfile_pic_real"] == "") {
                        postfile_pic_real = post["postfile_pic_real"];

                        html_temp = ` <div class="box post-box" id="${post["_id"]}">
<div class="post-image-box delete-post-content">
  <div class="delete-post" onclick="delete_post('${post["_id"]}')"></div>
</div>
  <img src="/static/${post["postfile_pic_real"]}" />
<article class="media post-media">
  <div class="media-left">
    <a class="image is-64x64" href="/user/${post["username"]}">
      <img
        class="is-rounded"
        src="/static/${post["profile_pic_real"]}"
        alt="Image"
      />
    </a>
  </div>
  <div class="media-content">
    <div class="content">
      <p>
        <strong class="post-content__name">${post["profile_name"]}</strong>
        <small class="post-content__username">@${post["username"]}</small> <small class="post-content__time">${time_before}</small>
        <br />
        <p class="post-content__comment">${post["comment"]}</p>
      </p>
    </div>
    <nav class="level is-mobile">
      <div class="level-left">
        <a
          class="level-item is-sparta"
          aria-label="heart"
          onclick="toggle_like('${post["_id"]}', 'heart')"
        >
          <span class="icon is-small"
            ><i class="fa ${class_heart}" aria-hidden="true"></i></span
          >&nbsp;<span class="like-num"
            >${num2str(post["count_heart"])}</span

          >
        </a>
        <button class="comment-button" onclick='$("#comment-area${i}").toggleClass("active")'></button>
          <dl>
            <div>
                <dt class="sr-only">댓글 수</dt>
                <dd class="commnet-count">${commentCounts}</dd>
            </div>
                <div>
                <dt class="sr-only">좋아요 한 사람</dt>
                <dd>  ${likes_temp} </dd>
                </div>
        </dl>
       
      </div>
    </nav>
  </div>
</article>

    </div>




  <div class="comment-area" id="comment-area${i}">
        ${comment_temp}   
   </div>




<div class="media-content comment-content">
  <div class="field">
    <p class="control">
      <textarea
        id="comment-post${i}"
        class="textarea comment-input"
        placeholder="칭찬 댓글을 남겨주세요!"
      ></textarea>
    </p>
    <nav class="level is-mobile">
      <div class="level-left"></div>
      <div class="level-right">
        <div class="level-item">
          <a class="button is-sparta post-button" onclick="commentPost(${i}, '${
                            post["_id"]
                        }')">댓글 등록</a>
        </div>
      </div>
    </nav>
  </div>
</div>`;
                    } else {
                        html_temp = ` <div class="box post-box" id="${post["_id"]}">
<div class="post-image-box delete-post-content">
  <div class="delete-post" onclick="delete_post('${post["_id"]}')"></div>
</div>

<article class="media post-media">
  <div class="media-left">
    <a class="image is-64x64" href="/user/${post["username"]}">
      <img
        class="is-rounded"
        src="/static/${post["profile_pic_real"]}"
        alt="Image"
      />
    </a>
  </div>
  <div class="media-content">
    <div class="content">
      <p>
        <strong class="post-content__name">${post["profile_name"]}</strong>
        <small class="post-content__username">@${post["username"]}</small> <small class="post-content__time">${time_before}</small>
        <br />
        <p class="post-content__comment">${post["comment"]}</p>
      </p>
    </div>
    <nav class="level is-mobile">
      <div class="level-left">
        <a
          class="level-item is-sparta"
          aria-label="heart"
          onclick="toggle_like('${post["_id"]}', 'heart')"
        >
          <span class="icon is-small"
            ><i class="fa ${class_heart} " aria-hidden="true"></i></span
          >&nbsp;<span class="like-num"
            >${num2str(post["count_heart"])}</span
          >
        </a>
      <button class="comment-button"  onclick='$("#comment-area${i}").toggleClass("active")'></button>
      <dl>
<div>
                <dt class="sr-only">댓글 수</dt>
                <dd class="commnet-count">${commentCounts}</dd>
            </div>
                <div>
                <dt class="sr-only">좋아요 한 사람</dt>
                <dd>  ${likes_temp} </dd>
                </div>
</dl>

      </div>
    </nav>
  </div>
</article>

        </div>

  <div class="comment-area" id="comment-area${i}">
        ${comment_temp}   
   </div>


<div class="media-content comment-content">
  <div class="field">
    <p class="control">
      <textarea
        id="comment-post${i}"
        class="textarea comment-input"
        placeholder="칭찬 댓글을 남겨주세요!"
      ></textarea>
    </p>
    <nav class="level is-mobile">
      <div class="level-left"></div>
      <div class="level-right">
        <div class="level-item">
          <a class="button is-sparta post-button" onclick="commentPost(${i}, '${
                            post["_id"]
                        }')">댓글 등록</a>
        </div>
      </div>
    </nav>
  </div>
</div>`;
                    }

                    $("#post-box").append(html_temp);
                }
            }
        },
    });
}

function time2str(date) {
    let today = new Date();
    let time = (today - date) / 1000 / 60; // 분

    if (time < 60) {
        return parseInt(time) + "분 전";
    }
    time = time / 60; // 시간
    if (time < 24) {
        return parseInt(time) + "시간 전";
    }
    time = time / 24;
    if (time < 7) {
        return parseInt(time) + "일 전";
    }
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`;
}

function num2str(count) {
    if (count > 10000) {
        return parseInt(count / 1000) + "k";
    }
    if (count > 500) {
        return parseInt(count / 100) / 10 + "k";
    }
    if (count == 0) {
        return "";
    }
    return count;
}

function toggle_like(post_id, type) {
    console.log(post_id, type);
    let $a_like = $(`#${post_id} a[aria-label='${type}']`);
    let $i_like = $a_like.find("i");
    let class_s = {heart: "fa-heart", star: "fa-star", like: "fa-thumbs-up"};
    let class_o = {
        heart: "fa-heart-o",
        star: "fa-star-o",
        like: "fa-thumbs-o-up",
    };
    if ($i_like.hasClass(class_s[type])) {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "unlike",
            },
            success: function (response) {
                console.log("unlike");
                $i_like.addClass(class_o[type]).removeClass(class_s[type]);
                $a_like.find("span.like-num").text(num2str(response["count"]));
            },
        });
    } else {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "like",
            },
            success: function (response) {
                console.log("like");
                $i_like.addClass(class_s[type]).removeClass(class_o[type]);
                $a_like.find("span.like-num").text(num2str(response["count"]));
            },
        });
    }
}

function give_me_my_file(value) {
    let path_array = value.split("\\", 3);
    let file_name = path_array[2];
    $(".file-name").text(file_name);
}


function delete_post(id) {

    let post_id = id

    $.ajax({
        type: "POST",
        url: "/del_post",
        data: {
            post_id_give: post_id
        },
        success: function (response) {
            alert(response['msg']);
            window.location.reload();
        },
    });

}

function onHover() {
    $("#header-logo").attr('src', '../static/logo_hover.png');
}

function offHover() {
    $("#header-logo").attr('src', '../static/logo.png');
}
