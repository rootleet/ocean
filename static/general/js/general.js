function delete_document(document_id) {
    Swal.fire({
      title: 'Delete Document?',
      showDenyButton: true,
      showCancelButton: false,
      confirmButtonText: 'YES',
      denyButtonText: `NO`,
    }).then((result) => {
      /* Read more about isConfirmed, isDenied below */
      if (result.isConfirmed) {
        Swal.fire('Process Completed','','success')
      } else if (result.isDenied) {
        Swal.fire('Changes are not saved', '', 'info')
      }
    })
}