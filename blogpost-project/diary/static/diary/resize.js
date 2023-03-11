// Get the file input element
const input = document.getElementById('id_image');

// Listen for the "change" event on the file input
input.addEventListener('change', (event) => {
    // Get the selected file
    const file = event.target.files[0];
    console.log(file);
    // Create a new FileReader object
    const reader = new FileReader();

    // Set the onload event handler
    reader.onload = (event) => {
        // Create a new image object
        const img = new Image();

        // Set the onload event handler
        img.onload = () => {
            // Set the maximum size of the image
            const max_size = 800;

            // Calculate the new width and height while maintaining aspect ratio
            let width, height;
            if (img.width > img.height) {
                width = max_size;
                height = img.height * (max_size / img.width);
            } else {
                height = max_size;
                width = img.width * (max_size / img.height);
            }

            // Create a canvas element
            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;

            // Draw the resized image onto the canvas
            const context = canvas.getContext('2d');
            context.drawImage(img, 0, 0, width, height);

            // Get the resized image as a data URL
            const dataUrl = canvas.toDataURL(file.type);

            // Create a new File object from the data URL
            const resizedFile = dataUrlToFile(dataUrl, file.name);

            // Replace the original file with the resized file
            event.target.result = resizedFile;
        };

        // Set the source of the image object to the selected file
        img.src = event.target.result;
    };

    // Read the selected file as a data URL
    reader.readAsDataURL(file);

    // Replace the original file with the resized file
    event.target.files[0] = event.target.result;
});

// Function to convert a data URL to a File object
function dataUrlToFile(dataUrl, fileName) {
    const arr = dataUrl.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], fileName, { type: mime });
}