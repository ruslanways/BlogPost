document.getElementById('id_image').addEventListener('change', function(event) {
    var file = event.target.files[0];
    var options = { maxWidth: 800, maxHeight: 600, canvas: true }; // set your desired image size here
    loadImage(file, function(img) {
        // create a canvas element to draw the resized image onto
        var canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        canvas.getContext('2d').drawImage(img, 0, 0, img.width, img.height);
        // convert the canvas back to a Blob object for uploading
        canvas.toBlob(function(blob) {
            // replace the original file with the resized version
            event.target.files[0] = new File([blob], file.name, { type: file.type });
        }, file.type);
    }, options);
});
