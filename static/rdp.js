(function() {
	function mouseButtonMap(button) {
		switch(button) {
		case 0:
			return 0;
		case 2:
			return 1;
		default:
			return -1;
		}
	};

	function Client(canvas) {
		this.canvas = canvas;
		// create renderer
		this.render = new Mstsc.Canvas.create(this.canvas);
		this.socket = null;
		this.activeSession = false;
		this.install();
	}
	
	Client.prototype = {
		install : function () {
			var self = this;
			// bind mouse move event
			this.canvas.addEventListener('mousemove', function (e) {
				if (!self.socket || !self.activeSession) return;
				
				var offset = Mstsc.elementOffset(self.canvas);
				self.socket.send(JSON.stringify({
					event: 'mouse',
					x: e.clientX - offset.left,
					y: e.clientY - offset.top,
					button: -1,
					isPressed: false,
				}));

				e.preventDefault();
				return false;
			});
			this.canvas.addEventListener('mousedown', function (e) {
				if (!self.socket) return;
				
				var offset = Mstsc.elementOffset(self.canvas);
				self.socket.send(JSON.stringify({
					event: 'mouse',
					x: e.clientX - offset.left,
					y: e.clientY - offset.top,
					button: mouseButtonMap(e.button),
					isPressed: true,
				}));
				e.preventDefault();
				return false;
			});
			this.canvas.addEventListener('mouseup', function (e) {
				if (!self.socket || !self.activeSession) return;
				
				var offset = Mstsc.elementOffset(self.canvas);
				self.socket.send(JSON.stringify({
					event: 'mouse',
					x: e.clientX - offset.left,
					y: e.clientY - offset.top,
					button: mouseButtonMap(e.button),
					isPressed: false,
				}));
				e.preventDefault();
				return false;
			});
			this.canvas.addEventListener('contextmenu', function (e) {
				if (!self.socket || !self.activeSession) return;
				
				var offset = Mstsc.elementOffset(self.canvas);
				self.socket.send(JSON.stringify({
					event: 'mouse',
					x: e.clientX - offset.left,
					y: e.clientY - offset.top,
					button: mouseButtonMap(e.button),
					isPressed: false,
				}));

				e.preventDefault();
				return false;
			});
			
			// bind keyboard event
			window.addEventListener('keydown', function (e) {
				if (!self.socket || !self.activeSession) return;

				self.socket.send(JSON.stringify({
					event: 'scancode',
					code: Mstsc.scancode(e),
					isPressed: true,
				}));

				e.preventDefault();
				return false;
			});
			window.addEventListener('keyup', function (e) {
				if (!self.socket || !self.activeSession) return;
				
				self.socket.send(JSON.stringify({
					event: 'scancode',
					code: Mstsc.scancode(e),
					isPressed: false,
				}));
				
				e.preventDefault();
				return false;
			});
			
			return this;
		},
		connect : function () {
			// WebSocket endpoint URL
			var wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
			var wsUrl = wsProtocol + '//localhost:8000/rdp/ws';

			var count = 0;
			var self = this;
			this.socket = new WebSocket(wsUrl);
			
			this.socket.addEventListener('open', function() {
				console.log('[mstsc.js] WebSocket connected');
				self.activeSession = false;

				console.log(self.canvas);

				// emit infos event
				self.socket.send(JSON.stringify({
					event: 'infos',
					screen: { 
						width: self.canvas.width, 
						height: self.canvas.height 
					}, 
					// locale: Mstsc.locale()
				}));
			});
			
			this.socket.addEventListener('message', function(event) {
				count += 1;
				if (count > 1000){
					self.activeSession = true;
				}
				var bitmap = JSON.parse(event.data);
				self.render.update(bitmap);
			});

			this.socket.addEventListener('close', function() {
				console.log('[mstsc.js] WebSocket connection closed');
				self.activeSession = false;
			});
		}
	}
	
	Mstsc.client = {
		create : function (canvas) {
			return new Client(canvas);
		}
	}
})();

function waitForObject(objName, callback) {
	const interval = setInterval(() => {
		if (typeof window[objName] !== 'undefined') {
			clearInterval(interval);
			callback(window[objName]);
		}
	}, 100); // 100ms 마다 확인
}

// 사용 예시
waitForObject('Mstsc', () => {
	var client = Mstsc.client.create(Mstsc.$("desktop"));
	client.connect();
});
