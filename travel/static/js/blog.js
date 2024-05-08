document.onreadystatechange = function () {
  var state = document.readyState
  if (state == 'complete') {
     document.getElementById('interactive');
     document.getElementById('preload').style.opacity="0";
     setTimeout(function(){
         document.getElementById('preload').style.visibility="hidden";
      },400);
  }
}