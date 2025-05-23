() => {
  console.log('ran function to inject print button');

  const printButton = document.getElementById("print-readme-button");

  if ((printButton) && printButton.offsetParent !== null) return;

  console.log('1st check passed');

  // find the rendered README container
  let readmeProse = document.querySelectorAll(".readme-markdown .prose");

  // skip if none
  if (readmeProse.length === 0) {
    console.debug("print button: readme container not found – skipping");
    return;
  }

  console.log('2nd check passed');

  // find the first element that is visible
  let found = false
  for (let i = 0; i < readmeProse.length; i++) {
    if (readmeProse[i].offsetParent !== null) {
      readmeProse = readmeProse[i];
      found = true;
      break;
    }
  }

  if (!found) {
    console.debug("readme container not found – skipping");
    return;
  }

  // build the button
  const btn = document.createElement("button");
  btn.className = "print-readme-button";
  btn.textContent = "🖨️ Print README";
  btn.style.cssText = "margin-top: 10px; padding: 8px; font-size: 14px;";

  btn.onclick = () => {
    // use string concatenation instead of backticks
    const html =
      "<html><head><title>Printable README</title>" +
      "<style>" + `
  /* ----------------------------------------
     Base setup: use a readable serif font,
     remove backgrounds, ensure black text
     ---------------------------------------- */
  * {
    background: transparent !important;
    color: #000 !important;
  }
  body {
    margin: 1in;                     /* 1-inch page margins */
    font-family: Georgia, serif;     /* classic printed‐doc font */
    font-size: 12pt;
    line-height: 1.5;
  }

  /* ----------------------------------------
     Headings: clear hierarchy, avoid
     page‐breaks immediately after
     ---------------------------------------- */
  h1, h2, h3, h4, h5, h6 {
    page-break-after: avoid;
    orphans: 3;
    widows: 3;
  }
  h1 { font-size: 24pt; margin: 0.67em 0; }
  h2 { font-size: 18pt; margin: 0.83em 0; }
  h3 { font-size: 16pt; margin: 1em 0; }
  h4 { font-size: 14pt; margin: 1.2em 0; }
  h5 { font-size: 12pt; margin: 1.5em 0; }
  h6 { font-size: 10pt; margin: 1.5em 0; }

  /* ----------------------------------------
     Paragraphs & blockquotes
     ---------------------------------------- */
  p {
    margin: 0 0 1em;   /* space after each paragraph */
  }
  blockquote {
    margin: 0.5em 1em;
    padding-left: 1em;
    border-left: 3px solid #000;
    font-style: italic;
  }

  /* ----------------------------------------
     Lists: indent & space
     ---------------------------------------- */
  ul, ol {
    margin: 0 0 1em 2em;
  }
  li {
    margin: 0.2em 0;
  }

  /* ----------------------------------------
     Code & preformatted blocks
     ---------------------------------------- */
  code, pre {
    font-family: Consolas, "Courier New", monospace;
    background-color: #f9f9f9;
    border: 1px solid #ccc;
    padding: 0.1em 0.3em;
  }
  pre {
    white-space: pre-wrap;             /* wrap long lines */
    word-break: break-word;
    margin: 0.5em 0;
    page-break-inside: avoid;
  }

  /* ----------------------------------------
     Tables: full‐width, simple borders
     ---------------------------------------- */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    page-break-inside: avoid;
  }
  th, td {
    border: 1px solid #000;
    padding: 0.2em 0.5em;
    text-align: left;
  }
  th {
    background-color: #eaeaea;
  }

  /* ----------------------------------------
     Links & images
     ---------------------------------------- */
  a {
    color: #000;
    text-decoration: underline;
  }
  img {
    max-width: 100%;
    page-break-inside: avoid;
    margin: 0.5em 0;
  }

  /* ----------------------------------------
     Horizontal rules
     ---------------------------------------- */
  hr {
    border: none;
    border-top: 1px solid #000;
    margin: 1em 0;
  }
` +
        /* "body{font-family:sans-serif;padding:1in;color:black;background:white;}" + */
        "*{box-sizing:border-box;}" +
      "</style>" +
      "</head><body>" +
      readmeProse.innerHTML +
      "</body></html>";

    const w = window.open("", "_blank");
    if (w) {
      w.document.write(html);
      w.document.close();
      w.focus();
      w.print();
    }
  };

  // inject right after the prose
  // Check if a print button already exists after the prose
  const nextElem = readmeProse.nextElementSibling;
  if (nextElem && nextElem.classList.contains("print-readme-button")) {
    console.log("print button already exists after prose – skipping injection");
  } else {
    readmeProse.insertAdjacentElement("afterend", btn);
    console.log("print button injected");
  }
}