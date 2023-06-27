const modalDisplayer = () => {
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
                                <form action="" class="accord" id="login">
                                    <p class="f-w-600 f-s-20">SIGN IN TO YOUR ACCOUNT</p>
                                    <p class="p-5-0 f-s-15 fade">Enter your details below to login</p>
                                    <div class="p-10-0">
                                        <div class="p-0">
                                            <p class="p-b-10 f-s-14">Email</p>
                                            <div class="b-one">
                                                <input type="text" class="b-n p-10"  name="" id="">
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
                                                <input type="text" class="b-n p-10"  name="" id="">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="btn p-10-0 siteButton ">
                                        <button class="w-p-100">Sign in</button>
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
                                        <form action="" method="" id="studentSignup">
                                        <small id="success"></small>
                                            <div class="p-10-0">
                                                <div class="p-0">
                                                    <p class="p-b-10 f-s-14">Username</p>
                                                    <div class="b-one">
                                                        <input type="text" class="b-n p-10"  name="" id="studentUsername">
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="p-5-0">
                                                <div class="p-0">
                                                    <p class="p-b-10 f-s-14">Email</p>
                                                    <small style="color:red" id="emailError">Hii</small>
                                                    <div class="b-one">
                                                        <input type="text" class="b-n p-10"  name="" id="studentEmail">
                                                    </div>
                                                </div>
                                            </div>
                                            <small style="color:red" id="usernameError">Hii</small>
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

                                        <form action="" method="">
                                            <div class="p-10-0">
                                                <div class="p-0">
                                                    <p class="p-b-10 f-s-14">Tutor's Email</p>
                                                    <div class="b-one">
                                                        <input type="text" class="b-n p-10"  name="" id="">
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="p-5-0">
                                                <div class="p-0">
                                                    <p class="p-b-10 f-s-14">Tutor's Password</p>
                                                    
                                                    <div class="b-one">
                                                        <input type="text" class="b-n p-10"  name="" id="">
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
}