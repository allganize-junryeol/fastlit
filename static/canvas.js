/*
 * Copyright (c) 2015 Sylvain Peyrefitte
 *
 * This file is part of mstsc.js.
 *
 * mstsc.js is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

(function() {
	
	/**
	 * decompress bitmap from RLE algorithm
	 * @param	bitmap	{object} bitmap object of bitmap event of node-rdpjs
	 */
	function decompress (bitmap) {
		var fName = null;
		switch (bitmap.bitsPerPixel) {
		case 15:
			fName = 'bitmap_decompress_15';
			break;
		case 16:
			fName = 'bitmap_decompress_16';
			break;
		case 24:
			fName = 'bitmap_decompress_24';
			break;
		case 32:
			fName = 'bitmap_decompress_32';
			break;
		default:
			throw 'invalid bitmap data format';
		}
		
		var input = new Uint8Array(bitmap.data);
		var inputPtr = Module._malloc(input.length);
		var inputHeap = new Uint8Array(Module.HEAPU8.buffer, inputPtr, input.length);
		inputHeap.set(input);
		
		var output_width = bitmap.destRight - bitmap.destLeft + 1;
		var output_height = bitmap.destBottom - bitmap.destTop + 1;
		var ouputSize = output_width * output_height * 4;
		var outputPtr = Module._malloc(ouputSize);

		var outputHeap = new Uint8Array(Module.HEAPU8.buffer, outputPtr, ouputSize);

		var res = Module.ccall(fName,
			'number',
			['number', 'number', 'number', 'number', 'number', 'number', 'number', 'number'],
			[outputHeap.byteOffset, output_width, output_height, bitmap.width, bitmap.height, inputHeap.byteOffset, input.length]
		);
		
		var output = new Uint8ClampedArray(outputHeap.buffer, outputHeap.byteOffset, ouputSize);
		
		Module._free(inputPtr);
		Module._free(outputPtr);
		
		return { width : output_width, height : output_height, data : output };
	}
	
	/**
	 * Un compress bitmap are reverse in y axis
	 */
	function reverse (bitmap) {
		return { width : bitmap.width, height : bitmap.height, data : new Uint8ClampedArray(bitmap.data) };
	}

	/**
	 * Canvas renderer
	 * @param canvas {canvas} use for rendering
	 */
	function Canvas(canvas) {
		this.canvas = canvas;
		this.ctx = canvas.getContext("2d");
	}
	
	Canvas.prototype = {
		/**
		 * update canvas with new bitmap
		 * @param bitmap {object}
		 */
		update : function (bitmap) {
			var output = null;
			if (bitmap.isCompress) {
				output = decompress(bitmap);
			}
			else {
				output = reverse(bitmap);
			}
			console.log(bitmap);
			console.log(bitmap);

			function base64Decord(base64String) {
				var padding = '='.repeat((4 - base64String.length % 4) % 4);
				var base64 = (base64String + padding)
					.replace(/\-/g, '+')
					.replace(/_/g, '/');
				var rawData = window.atob(base64);
				var bufferArray = new Uint8Array(rawData.length);
				for (var i = 0; i < rawData.length; ++i) {
					bufferArray[i] = rawData.charCodeAt(i);
				}
				return bufferArray;
			}
			
			var base64Image = bitmap.image;
			var bufferArray = base64Decord(base64Image);
			
			var image = new Image();
			image.src = 'data:image/png;base64,' + btoa(String.fromCharCode.apply(null, bufferArray));
			
			var ctx = this.ctx
			image.onload = function() {
				ctx.drawImage(image, bitmap.x, bitmap.y);
			}
		}
	}

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
		Mstsc.Canvas = {
			create : function (canvas) {
				return new Canvas(canvas);
			}
		}
	});
	
})();
