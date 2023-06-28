var acc = document.getElementsByClassName("accordiontab");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function () {
    
    this.classList.toggle("active-accordion");
    var panel = this.nextElementSibling;

    var panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    }
  });
}

function tabsign(evt, tabname, tabbtn, tabcontent, local)
{
    var tabbutton, tabcontent, i;
    tabcontent = document.getElementsByClassName(tabcontent)
    for(i = 0; i< tabcontent.length; i++)
    {
        tabcontent[i].style.display = "none"
    }

    tabbutton = document.getElementsByClassName(tabbtn)

    for(i = 0; i< tabbutton.length; i++)
    {
        tabbutton[i].className =  tabbutton[i].className.replace(" activeS", "")
       
  
    }
    document.getElementById(tabname).style.display = "block"
    evt.currentTarget.className += " activeS"
    saveLocal(local, evt.currentTarget.id)

              
}


function tab1(evt, tabname, tabbtn, tabcontent, local)
{
    var tabbutton, tabcontent, i;
    tabcontent = document.getElementsByClassName(tabcontent)
    for(i = 0; i< tabcontent.length; i++)
    {
        tabcontent[i].style.display = "none"
    }

    tabbutton = document.getElementsByClassName(tabbtn)

    for(i = 0; i< tabbutton.length; i++)
    {
        tabbutton[i].className =  tabbutton[i].className.replace(" activeQ", "")
       
  
    }
    document.getElementById(tabname).style.display = "block"
    evt.currentTarget.className += " activeQ"
    saveLocal(local, evt.currentTarget.id)

              
}

function tab(evt, tabname, tabbtn, tabcontent, local)
{
    var tabbutton, tabcontent, i;
    tabcontent = document.getElementsByClassName(tabcontent)
    for(i = 0; i< tabcontent.length; i++)
    {
        tabcontent[i].style.display = "none"
    }

    tabbutton = document.getElementsByClassName(tabbtn)

    for(i = 0; i< tabbutton.length; i++)
    {
        tabbutton[i].className =  tabbutton[i].className.replace(" activeFaq", "")
       
  
    }
    document.getElementById(tabname).style.display = "block"
    evt.currentTarget.className += " activeFaq"
    saveLocal(local, evt.currentTarget.id)
              
}
function getElem(res){
  var a, b, c, d , e, f;
  var a = document.getElementsByTagName("*");
  for(b = 0; b < a.length; b++){
      c = a[b];
      d = c.getAttribute(res);
      if(d){
          e = new XMLHttpRequest();
          e.onreadystatechange = function (){
              if(this.readyState == 4){
                  if(this.status == 200){
                      c.innerHTML = this.responseText;
                  }

                  c.removeAttribute(res);
                  getElem(res);
              }
          }
          e.open("GET", d, true);
          e.send();
          return;
      }
  }
}

autoPages("FAQLocal", "how-it-works-btn")
autoPages("QuizLocal", "all-btn")
autoPages("SignLocal", "login-btn")
autoPages("SignLocal", "login-btn")


function saveLocal(name, data)
{
  return localStorage.setItem(name, JSON.stringify(data))
}

function getLocal(name)
{
  return JSON.parse(localStorage.getItem(name))
}

function autoPages(name, defaultLocal)
{
  let Local = getLocal(name);
  if(Local == null)
  {
     saveLocal(name, defaultLocal)
     Local = defaultLocal;
  }
  console.log(Local);
  if(Local === null){
    document.getElementById(Local).click()
  }
  
}

function toogleSearch()
{
    $( ".search" ).toggleClass( "searchtransition" )
    $( ".search-mobile" ).toggleClass( "searchtransition" )
}

window.onscroll = ()=>{
    if(document.body.scrollTop > 40 || document.documentElement.scrollTop > 40)
    {
        $("header").addClass("headerBg")
    }
    else
    {
        $("header").removeClass("headerBg")
    }
}
          

setInterval(()=>{
  if(screen.width > 888)
  {
      $(".mobile").addClass("hide-m")
  }
  else
  {
      $(".mobile").removeClass("hide-m")
  }
}, 10)

const checkUsername = (username) => {
    const url = 'http://localhost:8000/student';
    const checkUserUrl = `${url}/${username}`;
  
    // Check if user with the username exists
    return fetch(checkUserUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
      .then(response => response.json())
      .then(user => {
        if (user) {
          return true; // Username already exists
        } else {
          return false; // Username does not exist
        }
      })
      .catch(error => {
        console.error('Error checking username:', error);
        throw error;
      });
  };

const checkEmail = (email) => {
    const url = 'http://localhost:8000/student';
    const checkUserUrl = `${url}/${email}`;
  
    // Check if user with the email exists
    return fetch(checkUserUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
      .then(response => response.json())
      .then(user => {
        if (user) {
          return true; // Email already exists
        } else {
          return false; // Email does not exist
        }
      })
      .catch(error => {
        console.error('Error checking email:', error);
        throw error;
      });
  };

  const createUser = (username, email, password) => {
    // First, check if the username already exists
    checkUsername(username)
      .then(usernameExists => {
        if (usernameExists) {
          console.log('Username already exists');
          // Handle existing username case here
        } else {
          // Username is available, now check if the email exists
          return checkEmail(email);
        }
      })
      .then(emailExists => {
        if (emailExists) {
          console.log('Email already exists');
          // Handle existing email case here
        } else {
          // Both username and email are available, proceed with creating the user
          const url = 'http://localhost:8000/student';
          const payload = {
            username: username,
            email: email,
            password: password
          };
  
          fetch(url, {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
          })
            .then(response => response.json())
            .then(data => {
              console.log('User created successfully:', data);
              // Handle successful user creation here
            })
            .catch(error => {
              console.error('Error creating user:', error);
              // Handle error while creating user here
            });
        }
      })
      .catch(error => {
        console.error('Error checking username or email:', error);
        // Handle error while checking username or email here
      });
  };
          
function openM()
{
   
   
    var htm = `
    <style>
        .accord, #usernameError, #emailError{
            display: none;
        }
        .spinning{
            opacity: .3;
        }
    </style>
    <div id="myModal" class="modal ">

        <div class="modal-content col-3">
        <div class="modal-header">
            <div class="p-20">
                <div class="p-20 bgwhite b-b-r-r-20 b-t-r-r-20 b-t-l-r-20">
                        <div class="">
                            <div>
                                <span class="close">&times;</span>
                                <div class="text-center">
                                    
                                </div>
                                <form action="/auth/login" class="accord" id="login" method="POST">
                                <small id="successfulSignin"></small>
                                    <p class="f-w-600 f-s-20">SIGN IN TO YOUR ACCOUNT</p>
                                    <p class="p-5-0 f-s-15 fade">Enter your details below to login</p>
                                    <div class="p-10-0">
                                        <div class="p-0">
                                            <p class="p-b-10 f-s-14">Email/Username</p>
                                            <div class="b-one">
                                                <input type="text" class="b-n p-10"  name="username" id="emailLogin">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="p-5-0">
                                        <div class="p-0">
                                            <div class="display-flex-normal space-between">
                                                <p class="p-b-10 f-s-14">Password</p>
                                                <a href="./forgetpassword.html">Forgot password?</a>
                                            </div>
                                            <div class="b-one">
                                                <input type="text" class="b-n p-10"  name="password" id="passwordLogin">
                                            </div>
                                        </div>
                                    </div>
                                    <small style="color:red" id="loginError"></small>
                                    <div class="btn p-10-0 siteButton ">
                                        <button class="w-p-100" id="studentSpinner">Sign in</button>
                                    </div>
                                    <div class="p-5-0">
                                        <div class="p-0">
                                            <div class="display-flex-normal space-between">
                                                <p class="p-b-10 f-s-14">Dont have an Account?</p>
                                                <a id="register-btn" onclick="tabsign(event, 'register', 'sign-btn', 'accord', 'SignLocal')" class="sgin-btn cursor-pointer" style="color: blue;">Register now</a>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="btn p-5-0 ">
                                    
                                        <button class="w-p-100 p-5-0 b-n bgwhite bs" ><i class="fa fa-google p-r-10" aria-hidden="true"></i>Continue with Google</button>
                                    </div>
                                    <div class="btn p-5-0 ">
                                        <button class="w-p-100 p-5-0 b-n bgwhite bs" ><i class="fa fa-facebook p-r-10" aria-hidden="true"></i>Continue with Facebook</button>
                                    </div>
                                </form>
                                <div class="">
                                    <p class="f-w-600 f-s-20">SIGN UP AN ACCOUNT</p>

                                    <div class="display-flex-normal">
                                        <button id="register-student-btn" class="col-6 p-10 bg-n b-one" onclick="tabsign(event, 'register', 'sign-btn', 'accord', 'SignLocal')">I'm a student</button>
                                        <button id="register-tutor-btn" class="col-6 p-10 bg-n b-one"  onclick="tabsign(event, 'register-tutor', 'sign-btn', 'accord', 'SignLocal')">I'm a tutor</button>
                                    </div>


                                    <div id="register"  class="accord ">
                                    
                                        <p class="p-5-0 f-s-15 fade">Sign up as a student</p>
                                        <form action="/student/create" method="POST" id="studentSignup">
                                        <small id="success"></small>
                                            <div class="p-10-0">
                                                <div class="p-0">
                                                    <p class="p-b-10 f-s-14">Username</p>
                                                    <div class="b-one">
                                                        <input type="text" class="b-n p-10"  name="username" id="studentUsername">
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="p-5-0">
                                                <div class="p-0">
                                                    <p class="p-b-10 f-s-14">Email</p>
                                                    <div class="b-one">
                                                        <input type="text" class="b-n p-10"  name="email" id="studentEmail">
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="btn p-10-0 siteButton ">
                                                <button class="w-p-100" id="studentSpinner">Register now</button>
                                            </div>
                                            <div class="display-flex-normal space-between">
                                                <p class="p-b-10 f-s-14">Already have an account?</p>
                                                <a  id="login-btn" onclick="tabsign(event, 'login', 'sign-btn', 'accord', 'SignLocal')" class="sgin-btn cursor-pointer">Login now</a>
                                            </div>
                                        </form>
                                    </div>


                                    <div id="register-tutor"  class="accord ">
                                        <p class="p-5-0 f-s-15 fade">Enter details to register as a tutor</p>

                                        <form action="/tutor/create" method="POST">
                                            <div class="p-10-0">
                                                <div class="p-0">
                                                    <p class="p-b-10 f-s-14">Tutor's Username</p>
                                                    <div class="b-one">
                                                        <input type="text" class="b-n p-10"  name="username" id="">
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="p-5-0">
                                                <div class="p-0">
                                                    <p class="p-b-10 f-s-14">Tutor's Email</p>
                                                    
                                                    <div class="b-one">
                                                        <input type="text" class="b-n p-10"  name="email" id="">
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="btn p-10-0 siteButton ">
                                                <button class="w-p-100">Register now</button>
                                            </div>
                                            <div class="display-flex-normal space-between">
                                                <p class="p-b-10 f-s-14">Already have an account?</p>
                                                <a  id="login-btn" onclick="tabsign(event, 'login', 'sign-btn', 'accord', 'SignLocal')" class="sgin-btn cursor-pointer">Login now</a>
                                            </div>
                                        </form>
                                    </div>


                                </div>
                            


                            </div>
                        </div>
                        
                    </div>
                </div>
            </div>
        </div>
    </div>

    
    `;


    const mosignup = document.querySelector(".mo-signup");
    mosignup.innerHTML = htm;

    const modal = document.getElementById("myModal");
    modal.style.display = "block";

    autoPages("SignLocal", "login-btn");


    const span = document.getElementsByClassName("close")[0];
    span.onclick = function() {
      modal.style.display = "none";
    }
    window.onclick = function(event) {
        if (event.target == modal) {
          modal.style.display = "none";
        }
    }
}