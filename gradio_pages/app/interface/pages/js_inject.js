(function addPrintButton() {
  // Avoid adding it multiple times
  if (document.getElementById("print-readme-button")) return;

  const btn = document.createElement("button");
  btn.textContent = "🖨️ Print README";
  btn.id = "print-readme-button";
  btn.style = "margin-top: 10px; padding: 8px; font-size: 14px;";

  btn.onclick = function () {
    const target = document.querySelector('#readme-markdown .prose');
    if (!target) {
      alert('Could not find #readme-markdown .prose');
    } else {
      const newWindow = window.open('', '_blank');
      newWindow.document.write(`
        <html>
          <head>
            <title>Printable README</title>
            <style>
              body {
                font-family: sans-serif;
                padding: 1in;
                color: black;
                background: white;
              }
              * {
                box-sizing: border-box;
              }
            </style>
          </head>
          <body>
            ${target.innerHTML}
          </body>
        </html>
      `);
      newWindow.document.close();
      newWindow.focus();
      newWindow.print();
    }
  };

  // Add it below the output section or root
  console.log('adding print button to the dom');
  const target = document.querySelector("body");
  target.appendChild(btn);
})();


