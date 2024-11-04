/**
 * Template Name: NiceAdmin
 * Template URL: https://bootstrapmade.com/nice-admin-bootstrap-admin-html-template/
 * Updated: Apr 20 2024 with Bootstrap v5.3.3
 * Author: BootstrapMade.com
 * License: https://bootstrapmade.com/license/
 */

(function () {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim();
    if (all) {
      return [...document.querySelectorAll(el)];
    } else {
      return document.querySelector(el);
    }
  };

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    if (all) {
      select(el, all).forEach((e) => e.addEventListener(type, listener));
    } else {
      select(el, all).addEventListener(type, listener);
    }
  };

  /**
   * Easy on scroll event listener
   */
  const onscroll = (el, listener) => {
    el.addEventListener("scroll", listener);
  };

  /**
   * Sidebar toggle
   */
  if (select(".toggle-sidebar-btn")) {
    on("click", ".toggle-sidebar-btn", function (e) {
      select("body").classList.toggle("toggle-sidebar");
    });
  }

  /**
   * Search bar toggle
   */
  if (select(".search-bar-toggle")) {
    on("click", ".search-bar-toggle", function (e) {
      select(".search-bar").classList.toggle("search-bar-show");
    });
  }

  /**
   * Navbar links active state on scroll
   */
  let navbarlinks = select("#navbar .scrollto", true);
  const navbarlinksActive = () => {
    let position = window.scrollY + 200;
    navbarlinks.forEach((navbarlink) => {
      if (!navbarlink.hash) return;
      let section = select(navbarlink.hash);
      if (!section) return;
      if (
        position >= section.offsetTop &&
        position <= section.offsetTop + section.offsetHeight
      ) {
        navbarlink.classList.add("active");
      } else {
        navbarlink.classList.remove("active");
      }
    });
  };
  window.addEventListener("load", navbarlinksActive);
  onscroll(document, navbarlinksActive);

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  let selectHeader = select("#header");
  if (selectHeader) {
    const headerScrolled = () => {
      if (window.scrollY > 100) {
        selectHeader.classList.add("header-scrolled");
      } else {
        selectHeader.classList.remove("header-scrolled");
      }
    };
    window.addEventListener("load", headerScrolled);
    onscroll(document, headerScrolled);
  }

  /**
   * Back to top button
   */
  let backtotop = select(".back-to-top");
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add("active");
      } else {
        backtotop.classList.remove("active");
      }
    };
    window.addEventListener("load", toggleBacktotop);
    onscroll(document, toggleBacktotop);
  }

  /**
   * Initiate tooltips
   */
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  /**
   * Initiate quill editors
   */
  if (select(".quill-editor-default")) {
    new Quill(".quill-editor-default", {
      theme: "snow",
    });
  }

  if (select(".quill-editor-bubble")) {
    new Quill(".quill-editor-bubble", {
      theme: "bubble",
    });
  }

  if (select(".quill-editor-full")) {
    new Quill(".quill-editor-full", {
      modules: {
        toolbar: [
          [
            {
              font: [],
            },
            {
              size: [],
            },
          ],
          ["bold", "italic", "underline", "strike"],
          [
            {
              color: [],
            },
            {
              background: [],
            },
          ],
          [
            {
              script: "super",
            },
            {
              script: "sub",
            },
          ],
          [
            {
              list: "ordered",
            },
            {
              list: "bullet",
            },
            {
              indent: "-1",
            },
            {
              indent: "+1",
            },
          ],
          [
            "direction",
            {
              align: [],
            },
          ],
          ["link", "image", "video"],
          ["clean"],
        ],
      },
      theme: "snow",
    });
  }

  /**
   * Initiate TinyMCE Editor
   */

  const useDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const isSmallScreen = window.matchMedia("(max-width: 1023.5px)").matches;

  tinymce.init({
    selector: "textarea.tinymce-editor",
    plugins:
      "preview importcss searchreplace autolink autosave save directionality code visualblocks visualchars fullscreen image link media codesample table charmap pagebreak nonbreaking anchor insertdatetime advlist lists wordcount help charmap quickbars emoticons accordion",
    editimage_cors_hosts: ["picsum.photos"],
    menubar: "file edit view insert format tools table help",
    toolbar:
      "undo redo | accordion accordionremove | blocks fontfamily fontsize | bold italic underline strikethrough | align numlist bullist | link image | table media | lineheight outdent indent| forecolor backcolor removeformat | charmap emoticons | code fullscreen preview | save print | pagebreak anchor codesample | ltr rtl",
    autosave_ask_before_unload: true,
    autosave_interval: "30s",
    autosave_prefix: "{path}{query}-{id}-",
    autosave_restore_when_empty: false,
    autosave_retention: "2m",
    image_advtab: true,
    link_list: [
      {
        title: "My page 1",
        value: "https://www.tiny.cloud",
      },
      {
        title: "My page 2",
        value: "http://www.moxiecode.com",
      },
    ],
    image_list: [
      {
        title: "My page 1",
        value: "https://www.tiny.cloud",
      },
      {
        title: "My page 2",
        value: "http://www.moxiecode.com",
      },
    ],
    image_class_list: [
      {
        title: "None",
        value: "",
      },
      {
        title: "Some class",
        value: "class-name",
      },
    ],
    importcss_append: true,
    file_picker_callback: (callback, value, meta) => {
      /* Provide file and text for the link dialog */
      if (meta.filetype === "file") {
        callback("https://www.google.com/logos/google.jpg", {
          text: "My text",
        });
      }

      /* Provide image and alt text for the image dialog */
      if (meta.filetype === "image") {
        callback("https://www.google.com/logos/google.jpg", {
          alt: "My alt text",
        });
      }

      /* Provide alternative source and posted for the media dialog */
      if (meta.filetype === "media") {
        callback("movie.mp4", {
          source2: "alt.ogg",
          poster: "https://www.google.com/logos/google.jpg",
        });
      }
    },
    height: 600,
    image_caption: true,
    quickbars_selection_toolbar:
      "bold italic | quicklink h2 h3 blockquote quickimage quicktable",
    noneditable_class: "mceNonEditable",
    toolbar_mode: "sliding",
    contextmenu: "link image table",
    skin: useDarkMode ? "oxide-dark" : "oxide",
    content_css: useDarkMode ? "dark" : "default",
    content_style:
      "body { font-family:Helvetica,Arial,sans-serif; font-size:16px }",
  });

  /**
   * Initiate Bootstrap validation check
   */
  var needsValidation = document.querySelectorAll(".needs-validation");

  Array.prototype.slice.call(needsValidation).forEach(function (form) {
    form.addEventListener(
      "submit",
      function (event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }

        form.classList.add("was-validated");
      },
      false
    );
  });

  /**
   * Initiate Datatables
   */
  const datatables = select(".datatable", true);
  datatables.forEach((datatable) => {
    new simpleDatatables.DataTable(datatable, {
      perPageSelect: [5, 10, 15, ["All", -1]],
      columns: [
        {
          select: 2,
          sortSequence: ["desc", "asc"],
        },
        {
          select: 3,
          sortSequence: ["desc"],
        },
        {
          select: 4,
          cellClass: "green",
          headerClass: "red",
        },
      ],
    });
  });

  /**
   * Autoresize echart charts
   */
  const mainContainer = select("#main");
  if (mainContainer) {
    setTimeout(() => {
      new ResizeObserver(function () {
        select(".echart", true).forEach((getEchart) => {
          echarts.getInstanceByDom(getEchart).resize();
        });
      }).observe(mainContainer);
    }, 200);
  }
})();

// Adding more file  course modal

document.getElementById("addCourseBtn").addEventListener("click", function () {
  const additionalCourses = document.getElementById("additional-courses");

  // Get values from the first course card
  const courseName = document.querySelector('input[name="course_name"]').value;
  const teacherId = document.querySelector('select[name="teacher_id"]').value;
  const department = document.querySelector('select[name="department"]').value;

  const newCard = `
      <div class="card mb-3">
          <div class="card-body">
              <div class="input-group mb-3">
                  <input type="file" name="file[]" class="form-control" accept="video/*" required>
              </div>
              <div class="input-group mb-3">
                <span class="input-group-text" id="basic-addon1"><i class="bi bi-list-ol"></i></span>
                <input type="number" class="form-control" placeholder="Sequence" name="sequence" min="1" required>
              </div>
              <div class="input-group mb-3">
                  <input class="form-control" placeholder="Title" name="title[]" required>
              </div>
              <div class="input-group mb-3">
                  <input type="file" name="thumbnail[]" class="form-control" id="fileupload" accept="image/*" required>
              </div>
              <div class="input-group mb-3">
                  <textarea class="form-control" placeholder="Write a short description" name="description[]" rows="4" required></textarea>
              </div>
              <!-- Hidden inputs to carry forward the same values for course name, teacher, and department -->
              <input type="hidden" name="course_name[]" value="${courseName}">
              <input type="hidden" name="teacher_id[]" value="${teacherId}">
              <input type="hidden" name="department[]" value="${department}">
              <button type="button" class="btn btn-danger remove-course">Remove</button>
          </div>
      </div>
  `;

  additionalCourses.insertAdjacentHTML("beforeend", newCard);

  // Attach remove event listener to newly added card
  additionalCourses
    .querySelectorAll(".remove-course")
    .forEach(function (button) {
      button.addEventListener("click", function () {
        button.closest(".card").remove();
      });
    });
});

// Role Card

function changeText(newText) {
  const sliderText = document.getElementById("slider");
  sliderText.classList.add("hidden"); // Add hidden class for fade out effect

  setTimeout(() => {
    sliderText.innerHTML = newText; // Change the text content
    sliderText.classList.remove("hidden"); // Fade in effect
  }, 400); // Adjust timing to match the transition
}

function on_teacher() {
  changeText("<b>Teacher:</b> Upload and manage your lessons.");
}

function on_students() {
  changeText("<b>Student:</b> Explore lessons and track your progress.");
}

function on_admin() {
  changeText("<b>Admin:</b> Manage lessons and user activity.");
}
function resetText() {
  changeText(
    " <b> Hey there!  </b>  Let's get started—pick a role that suits you! "
  );
}

// --------------------------------------------------------------
// # VIDEO
// --------------------------------------------------------------

function playVideo(videoId) {
  const video = document.getElementById(videoId);
  if (video) {
    video.play();
  }
}

function pauseVideo(videoId) {
  const video = document.getElementById(videoId);
  if (video) {
    video.pause();
    video.currentTime = 0; // Resets the video to the beginning
  }
}
function displayFileNames(files, inputType) {
  const fileList = document.getElementById("uploadFileList");
  const videoPreviewContainer = document.getElementById(
    "videoPreviewContainer"
  );

  // Clear previous video previews
  if (inputType === "video") {
    fileList.innerHTML = "";
    videoPreviewContainer.innerHTML = "";
  }

  // Only process the first file
  if (files.length > 0) {
    const file = files[0];
    const fileName = file.name;
    const fileType = file.type;

    if (inputType === "video") {
      // Display the video file name with a remove button
      const fileItem = document.createElement("div");
      fileItem.className =
        "video-file-name d-flex justify-content-between align-items-start";
      fileItem.innerHTML = `
          <p class="text-muted">${fileName}</p>
          <button class="btn custom-close-btn" onclick="removeFile(this)">&#10005</button>
        `;
      fileList.appendChild(fileItem);

      // Only create a video preview if the file is a video
      if (fileType.startsWith("video/")) {
        const videoElement = document.createElement("video");
        videoElement.src = URL.createObjectURL(file);
        videoElement.controls = true;
        videoElement.width = 300; // Set width for video preview
        videoPreviewContainer.appendChild(videoElement);
      }
    } else if (inputType === "pdf") {
      // Update the value of the PDF file input field with the file name
      const relatedFileInput = document.getElementById("relatedFileInput");
      relatedFileInput.value = fileName; // Set the file name in the input field
    }
  }
}

function removeFile(button) {
  const fileList = document.getElementById("uploadFileList");
  const videoPreviewContainer = document.getElementById(
    "videoPreviewContainer"
  );

  // Remove the corresponding file name and preview
  const fileItem = button.parentElement;
  fileList.removeChild(fileItem);
  videoPreviewContainer.innerHTML = ""; // Clear video preview
}

function nextTab() {
  const tabs = document.querySelectorAll(".nav-tabs .nav-link-nav");
  const activeTab = document.querySelector(".nav-tabs .nav-link.active");
  let nextIndex = Array.from(tabs).indexOf(activeTab) + 1;

  if (nextIndex < tabs.length) {
    tabs[nextIndex].click();
  }
}

function prevTab() {
  const tabs = document.querySelectorAll(".nav-tabs .nav-links");
  const activeTab = document.querySelector(".nav-tabs .nav-link.active");
  let prevIndex = Array.from(tabs).indexOf(activeTab) - 1;

  if (prevIndex >= 0) {
    tabs[prevIndex].click();
  }
}

function toggleInputFields() {
  const fileType = document.getElementById("relatedFileType").value;
  const fileInputContainer = document.getElementById(
    "relatedFileInputContainer"
  );
  const linkInputContainer = document.getElementById(
    "relatedLinkInputContainer"
  );

  // Show/hide input fields based on the selected file type
  fileInputContainer.classList.toggle(
    "d-none",
    fileType !== "pdf" && fileType !== "image"
  );
  linkInputContainer.classList.toggle("d-none", fileType !== "link");
}
