const fileSelect = document.getElementById("fileSelect"),
    fileElem = document.getElementById("fileElem"),
    fileList = document.getElementById("fileList");

fileSelect.addEventListener("click", function (e) {
  if (fileElem) {
    fileElem.click();
  }
  e.preventDefault(); // prevent navigation to "#"
}, false);

fileElem.addEventListener("change", handleFiles, false); 

function handleFiles() {
  if (!this.files.length) {
    fileList.innerHTML = "<p>No files selected!</p>";
  } else {
    fileList.innerHTML = "";
    const list = document.createElement("ul");
    fileList.appendChild(list);
    for (let i = 0; i < this.files.length; i++) {
      const li = document.createElement("li");
      list.appendChild(li);
      
      const img = document.createElement("img");
      img.src = URL.createObjectURL(this.files[i]);
      //img.height = 60;
      img.onload = function() {
        URL.revokeObjectURL(this.src);
      }
      li.appendChild(img);
      const info = document.createElement("span");
      info.innerHTML = this.files[i].name + ": " + this.files[i].size + " bytes";
      li.appendChild(info);
    }
  }
}
/*var txt = '';
//var xmlhttp = new XMLHttpRequest();
xmlhttp.onreadystatechange = function(){
  if(xmlhttp.status == 200 && xmlhttp.readyState == 4){
    txt = xmlhttp.responseText;
  }
};
xmlhttp.open("GET","abc.txt",true);
xmlhttp.send();
*/