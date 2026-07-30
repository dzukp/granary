
mechanisms = {}
current = null

// --- Base class ---

function Mechanism(name, title) {
	this.name    = name
	this.title   = title ? title : name
	this.cmd     = getTag('main', name + '_cmd')
	this.timeout = getTag('main', name + '_timeout')
	this.status  = getTag('main', name + '_status')
	this.state   = getTag('main', name + '_state')
}

Mechanism.prototype.setEnable = function(enable) {
	this.cmd.setValue((enable ? 0x0004 : 0x0008))
}

// --- Engine ---

function Engine(name, title) {
	Mechanism.call(this, name, title)
}
Engine.prototype = Object.create(Mechanism.prototype)
Engine.prototype.constructor = Engine

Engine.prototype.start = function() {
	this.cmd.setValue(0x0001)
}

Engine.prototype.stop = function() {
	this.cmd.setValue(0x0002)
}

Engine.prototype.className = function() {
	return 'Engine'
}

// --- Valve ---

function Valve(name, title) {
	Mechanism.call(this, name, title)
}
Valve.prototype = Object.create(Mechanism.prototype)
Valve.prototype.constructor = Valve

Valve.prototype.open = function() {
	this.cmd.setValue(0x0001)
}

Valve.prototype.close = function() {
	this.cmd.setValue(0x0002)
}

Valve.prototype.className = function() {
	return 'Valve'
}

// --- Init ---

function init() {

	mechanisms['m1_2']  = new Engine('m1_2', 'Конвейер 1.2')
	mechanisms['m1_3']  = new Engine('m1_3', 'Конвейер 1.3')
	mechanisms['m1_4']  = new Engine('m1_4', 'Конвейер 1.4')
	mechanisms['m1_5']  = new Engine('m1_5', 'Конвейер 1.5')
	mechanisms['m1_6']  = new Engine('m1_6', 'Конвейер 1.6')
	mechanisms['m1_7']  = new Engine('m1_7', 'Конвейер 1.7')
	mechanisms['m1_8']  = new Engine('m1_8', 'Конвейер 1.8')
	mechanisms['m1_9']  = new Engine('m1_9', 'Конвейер 1.9')
	mechanisms['m1_10'] = new Engine('m1_10', 'Конвейер 1.10')
	mechanisms['m1_11'] = new Engine('m1_11', 'Конвейер 1.11')
	mechanisms['m1_12'] = new Engine('m1_12', 'Конвейер 1.12')
	mechanisms['m13_1'] = new Engine('m13_1', 'Вентилятор 13.1')
	mechanisms['m13_2'] = new Engine('m13_2', 'Вентилятор 13.2')
	mechanisms['m13_3'] = new Engine('m13_3', 'Вентилятор 13.3')
	mechanisms['m13_4'] = new Engine('m13_4', 'Вентилятор 13.4')
	mechanisms['m13_5'] = new Engine('m13_5', 'Вентилятор 13.5')
	mechanisms['m13_6'] = new Engine('m13_6', 'Вентилятор 13.6')
	mechanisms['m13_7'] = new Engine('m13_7', 'Вентилятор 13.7')
	mechanisms['m13_8'] = new Engine('m13_8', 'Вентилятор 13.8')
	mechanisms['m14']   = new Engine('m14', 'Вентилятор 14')
	mechanisms['m15_3'] = new Engine('m15_3', 'Вентилятор 15.3')
	mechanisms['m16_3'] = new Engine('m16_3', 'Шлюзовой затвор 16.3')
	mechanisms['m3_3']  = new Engine('m3_3', 'Нория 3.3')
	mechanisms['m3_4']  = new Engine('m3_4', 'Нория 3.4')
	mechanisms['m3_5']  = new Engine('m3_5', 'Нория 3.5')
	mechanisms['m3_6']  = new Engine('m3_6', 'Нория 3.6')
	mechanisms['m6_1']  = new Engine('m6_1', 'Конвейер 6.1')
	mechanisms['m6_2']  = new Engine('m6_2', 'Конвейер 6.2')
	mechanisms['m6_4']  = new Engine('m6_4', 'Конвейер 6.4')
	mechanisms['m6_5']  = new Engine('m6_5', 'Конвейер 6.5')
	mechanisms['m6_6']  = new Engine('m6_6', 'Конвейер 6.6')
	mechanisms['m6_7']  = new Engine('m6_7', 'Конвейер 6.7')
	mechanisms['m6_8']  = new Engine('m6_8', 'Конвейер 6.8')
	mechanisms['m6_9']  = new Engine('m6_9', 'Конвейер 6.9')
	mechanisms['m6_10'] = new Engine('m6_10', 'Конвейер 6.10')
	mechanisms['m6_11'] = new Engine('m6_11', 'Конвейер 6.11')
	mechanisms['m8_1']  = new Valve('m8_1', 'Задвижка 8.1')
	mechanisms['m8_2']  = new Valve('m8_2', 'Задвижка 8.2')
	mechanisms['m8_3']  = new Valve('m8_3', 'Задвижка 8.3')
	mechanisms['m8_4']  = new Valve('m8_4', 'Задвижка 8.4')
	mechanisms['m8_5']  = new Valve('m8_5', 'Задвижка 8.5')
	mechanisms['m8_6']  = new Valve('m8_6', 'Задвижка 8.6')
	mechanisms['m8_7']  = new Valve('m8_7', 'Задвижка 8.7')
	mechanisms['m8_8']  = new Valve('m8_8', 'Задвижка 8.8')
	mechanisms['m8_9']  = new Valve('m8_9', 'Задвижка 8.9')
	mechanisms['m8_10'] = new Valve('m8_10', 'Задвижка 8.10')
	mechanisms['m8_11'] = new Valve('m8_11', 'Задвижка 8.11')
	mechanisms['m8_12'] = new Valve('m8_12', 'Задвижка 8.12')
	mechanisms['m8_13'] = new Valve('m8_13', 'Задвижка 8.13')

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
	getGlobalVar('dlg_name').setStringData(current.title)

    if (current.className() == 'Valve') {
        getGlobalVar('dlg_pusk_btn').setStringData('Открыть')
        getGlobalVar('dlg_stop_btn').setStringData('Закрыть')
        getGlobalVar('dlg_sensor_name').setStringData('Концевики')
        getGlobalVar('dlg_is_valve').setBooleanData(true)
        getScreen('engine_dlg').getObject('lbl_state_valve').show()
        getScreen('engine_dlg').getObject('lbl_state_eng').hide()
        getScreen('engine_dlg').getObject('di_closed').show()
    }
	else {
        getGlobalVar('dlg_pusk_btn').setStringData('Пуск')
        getGlobalVar('dlg_stop_btn').setStringData('Стоп')
        getGlobalVar('dlg_sensor_name').setStringData('Работа')
        getGlobalVar('dlg_is_valve').setBooleanData(false)
        getScreen('engine_dlg').getObject('lbl_state_valve').hide()
        getScreen('engine_dlg').getObject('lbl_state_eng').show()
        getScreen('engine_dlg').getObject('di_closed').hide()
    }
}


function test() {
	getScreen('engine_dlg').getObject('pusk')

}


init();
