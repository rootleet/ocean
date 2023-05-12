$(document).ready(function() {
  var dropZone = $('#drop_zone');

  // Prevent default drag behaviors
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.on(eventName, function(e) {
      e.preventDefault();
      e.stopPropagation();
    });
  });

  // Highlight drop zone when item is dragged over it
  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.on(eventName, function() {
      dropZone.addClass('highlight');
    });
  });

  // Remove highlight when item is dragged away from drop zone
  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.on(eventName, function() {
      dropZone.removeClass('highlight');
    });
  });

  // Handle dropped files
  dropZone.on('drop', function(e) {
    var files = e.originalEvent.dataTransfer.files;
    handleFiles(files);
  });

  // Handle uploaded files
  function handleFiles(files) {
    var formData = new FormData();

    $.each(files, function(i, file) {
      formData.append('file[]', file);
    });

    Swal.fire({
      'html':`<div class="spinner-border" role="status">
            <span class="sr-only">Loading...</span>
          </div>
          `,
      showConfirmButton: false
    })

    $.ajax({
      url: '/dolphine/upload/',  // Replace with your own upload URL
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      success: function(response) {
        alert(response);
        location.reload()
      },
      error: function(xhr, status, error) {
        alert('Error uploading files: ' + error);
      }
    });
  }
});
