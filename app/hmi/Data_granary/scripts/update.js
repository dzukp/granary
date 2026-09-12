var last_counter = 0
function checkPythonConnect() {
	var counter = getTag('main', 'counter').getValue()
	getGlobalVar('python_connected').setBooleanData(counter != last_counter)
	last_counter = counter
}