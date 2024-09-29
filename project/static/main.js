(function () {
    console.log("ready!"); // sanity check
  })();
  
//   It selects all elements with the class entry and attaches a click event listener to each.
  const postElements = document.getElementsByClassName("entry");
  
  for (var i = 0; i < postElements.length; i++) {
    postElements[i].addEventListener("click", function () {
      const postId = this.getElementsByTagName("h2")[0].getAttribute("id");
      const node = this;
      fetch(`/delete/${postId}`)
        .then(function (resp) {
          return resp.json();
        })
        .then(function (result) {
          if (result.status === 1) {
            // The post element is removed from the DOM using node.parentNode.removeChild(node).
            node.parentNode.removeChild(node);
            console.log(result);
          }
          location.reload();
        })
        .catch(function (err) {
          console.log(err);
        });
    });
  }