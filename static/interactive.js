function barclick()
{
    if (document.getElementById("nav-links").style.display === "none")
    {
      document.getElementById("nav-links").style.display = "flex";
    }
    else 
    {
      document.getElementById("nav-links").style.display = "none";
    } 
}

function nextHandler()
{
    document.getElementById("form1").style.left="-900px";
    document.getElementById("form2").style.left="10%";
    document.getElementById("form1").style.transition="1s";
    document.getElementById("form2").style.transition="1s";
}

function backHandler()
{
    document.getElementById("form2").style.left="900px";
    document.getElementById("form1").style.left="10%";
    document.getElementById("form1").style.transition="1s";
    document.getElementById("form2").style.transition="1s";
}

function submitHandler()
{

}