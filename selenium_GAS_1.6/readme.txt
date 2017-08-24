Other things you need:
selenium-server-standalone-2.48.2.jar
pip3 for python
use pip3 to install python bindings for selenium
chromedriver and iedriver for selenium

How to run:
1. Make sure you are in the selenium directory
2. Start the selenium server as a hub on the pc running the test script
| java -jar selenium-server-standalone-2.48.2.jar -role hub
3. Start the selenium server as a node on all the pcs opening browsers. 
You should specify the path of your chromedriver with -Dwebdriver.chrome.driver
if the test cannot find your chromedriver.
| java -jar selenium-server-standalone-2.48.2.jar -role node -hub http://localhost:4444/register -maxSession 20 -browser "browserName=chrome,maxInstances=10" -Dwebdriver.chrome.driver=/opt/chrome_driver/chromedriver -browser "browserName=firefox,maxInstances=10"
4. python seleniumtest.py fp/InputFileAmpleConfig

Framework:
seleniumtest.py will read from InputFileAmpleConfig and set:
 Which platforms you will use
 Which browsers you will use
 Which testset you will use (InputFileAmpleTest)
It will spawn several subprocesses that will run seleniumtest.py that each
spawn their own browser and read from InputFileAmpleTest.
PARSER_Ample.py will read InputFileAmpleTest to determine which submodules to
call. Add your submodules there.
The tests use the xpaths file to generate a dictionary of name:xpath for 
the various webelements of Ample.
                                         InputFileAmpleTest
                                                |
                                                V   
InputFileAmpleConfig => seleniumtest.py -> seleniumtest.py subprocesses
    ____________________________________________| |\`-> {Firefox}
   |                                              \ `-> {Chrome}
   V                                               `--> {Internet Explorer}
PARSER_Ample.py -> TEST_AmpleLogin.py    <= InputFileAmpleLogin
   |   A        -> TEST_AmpleDevMan.py   <= InputFileAmpleDevMan
   |   |        -> TEST_AmpleLineMon.py  <= InputFileAmpleLineMon
   |   |        -> TEST_AmpleSysAdmin.py <= InputFileAmpleSysAdmin
   |   |____________________|
   V
Generate test_report.csv for each platform/browser combination
   |
   `-> seleniumtest.py -> merge all the test reports into one test_report.csv
