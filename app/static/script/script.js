var btnsAbrirPopup = document.getElementsByClassName('btnAbrirPopup');
var btnFecharPopup = document.getElementById('btnFecharPopup');

var popup = document.getElementById('popup');

for (var i = 0; i < btnsAbrirPopup.length; i++) {
  btnsAbrirPopup[i].addEventListener('click', function() {
    popup.style.display = 'block';
  });
}

btnFecharPopup.addEventListener('click', function() {
  popup.style.display = 'none';}
);