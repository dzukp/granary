
mechanisms = {}
current = null

// --- Base class ---

function Mechanism(name) {
	this.name    = name
	this.cmd     = getTag('main', name + '_cmd')
	this.timeout = getTag('main', name + '_timeout')
	this.status  = getTag('main', name + '_status')
	this.state   = getTag('main', name + '_state')
}

Mechanism.prototype.setEnable = function(enable) {
	this.cmd.setValue((enable ? 0x0004 : 0x0008))
}

// --- Engine ---

function Engine(name) {
	Mechanism.call(this, name)
}
Engine.prototype = Object.create(Mechanism.prototype)
Engine.prototype.constructor = Engine

Engine.prototype.start = function() {
	this.cmd.setValue(0x0001)
}

Engine.prototype.stop = function() {
	this.cmd.setValue(0x0002)
}

// --- Valve ---

function Valve(name) {
	Mechanism.call(this, name)
}
Valve.prototype = Object.create(Mechanism.prototype)
Valve.prototype.constructor = Valve

Valve.prototype.open = function() {
	this.cmd.setValue(0x0001)
}

Valve.prototype.close = function() {
	this.cmd.setValue(0x0002)
}

// --- Init ---

function init() {

	mechanisms['m1_2']  = new Engine('m1_2')
	mechanisms['m1_3']  = new Engine('m1_3')
	mechanisms['m3_4']  = new Engine('m3_4')
	mechanisms['m13_1'] = new Engine('m13_1')
	mechanisms['m3_5']  = new Engine('m3_5')
	mechanisms['m3_6']  = new Engine('m3_6')
	mechanisms['m6_10'] = new Engine('m6_10')
	mechanisms['m6_9']  = new Engine('m6_9')
	mechanisms['m3_3']  = new Engine('m3_3')
	mechanisms['m14']   = new Engine('m14')
	mechanisms['m13_2'] = new Engine('m13_2')
	mechanisms['m13_3'] = new Engine('m13_3')
	mechanisms['m13_4'] = new Engine('m13_4')
	mechanisms['m13_5'] = new Engine('m13_5')
	mechanisms['m13_6'] = new Engine('m13_6')
	mechanisms['m13_7'] = new Engine('m13_7')
	mechanisms['m13_8'] = new Engine('m13_8')
	mechanisms['m1_4']  = new Engine('m1_4')
	mechanisms['m6_1']  = new Engine('m6_1')
	mechanisms['m1_8']  = new Engine('m1_8')
	mechanisms['m1_7']  = new Engine('m1_7')
	mechanisms['m6_2']  = new Engine('m6_2')
	mechanisms['m1_6']  = new Engine('m1_6')
	mechanisms['m1_5']  = new Engine('m1_5')
	mechanisms['m1_9']  = new Engine('m1_9')
	mechanisms['m1_10'] = new Engine('m1_10')
	mechanisms['m1_11'] = new Engine('m1_11')
	mechanisms['m1_12'] = new Engine('m1_12')
	mechanisms['m6_5']  = new Engine('m6_5')
	mechanisms['m6_11'] = new Engine('m6_11')
	mechanisms['m6_4']  = new Engine('m6_4')
	mechanisms['m6_6']  = new Engine('m6_6')
	mechanisms['m6_8']  = new Engine('m6_8')
	mechanisms['m16_3'] = new Engine('m16_3')
	mechanisms['m15_3'] = new Engine('m15_3')
	mechanisms['m6_7']  = new Engine('m6_7')
	mechanisms['m8_9']  = new Valve('m8_9')
	mechanisms['m8_8']  = new Valve('m8_8')
	mechanisms['m8_2']  = new Valve('m8_2')
	mechanisms['m8_7']  = new Valve('m8_7')
	mechanisms['m8_12'] = new Valve('m8_12')
	mechanisms['m8_13'] = new Valve('m8_13')
	mechanisms['m8_10'] = new Valve('m8_10')
	mechanisms['m8_11'] = new Valve('m8_11')
	mechanisms['m8_1']  = new Valve('m8_1')
	mechanisms['m8_5']  = new Valve('m8_5')
	mechanisms['m8_6']  = new Valve('m8_6')
	mechanisms['m8_3']  = new Valve('m8_3')
	mechanisms['m8_4']  = new Valve('m8_4')
}


function open(mech) {
	mechanisms[mech].open();
}

function close(mech) {
	mechanisms[mech].close();
}


function start(mech) {
	mechanisms[mech].start();
}


function stop(mech) {
	mechanisms[mech].stop();
}


function showDlg(mech_name) {
	//scadaList(getScreen('engine_dlg'), true);
	current = mechanisms[mech_name];
	scadaPrint('dialog ' + mech_name + ' ' + current)
	getGlobalVar('dlg_cmd').setBindSpeaker(current.cmd)
	getGlobalVar('dlg_status').setBindSpeaker(current.status)
	getGlobalVar('dlg_timeout').setBindSpeaker(current.timeout)
	getGlobalVar('dlg_state').setBindSpeaker(current.state)
	getGlobalVar('dlg_name').setStringData(mech_name)
//	getScreen('engine_dlg').showNormal();
}


init();
