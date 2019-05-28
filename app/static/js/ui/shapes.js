// This is a simple library for drawing and animating a pentagon-based pattern
// in a canvas. You can use it as follows:
//
//     var myCanvas = document.getElementById(...);
//     var shapes = new window.shapesHolder.Shapes(myCanvas);
//     shapes.begin();
//
// It is your responsibility to resize the canvas as needed.

(function() {

    function Animation(start, end, duration) {
      this.start = start;
      this.end = end;
      this.duration = duration;
      this.timestamp = (new Date()).getTime();
    }
  
    Animation.prototype.elapsed = function() {
      return ((new Date()).getTime()-this.timestamp)/1000;
    };
  
    Animation.prototype.intermediate = function(pg) {
      var percentage = Math.min(this.elapsed() / this.duration, 1);
      pg.x = this.start.x + (this.end.x-this.start.x)*percentage;
      pg.y = this.start.y + (this.end.y-this.start.y)*percentage;
      pg.radius = this.start.radius +
        (this.end.radius-this.start.radius)*percentage;
      pg.rotation = this.start.rotation +
        (this.end.rotation-this.start.rotation)*percentage;
      pg.opacity = this.start.opacity +
        (this.end.opacity-this.start.opacity)*percentage;
    };
  
    Animation.prototype.isDone = function() {
      return this.elapsed() >= this.duration;
    };
  
    function MovingShape(initial) {
      this.pentagon = initial.copy();
      this.animation = new Animation(initial, initial, 0);
    }
  
    function Shape(x, y, radius, rotation, opacity, numSides) {
      this.x = x;
      this.y = y;
      this.radius = radius;
      this.rotation = rotation;
      this.opacity = opacity;
      this.numSides = numSides;
    }
  
    Shape.prototype.copy = function() {
      return new Shape(this.x, this.y, this.radius, this.rotation,
        this.opacity, this.numSides);
    };
  
    Shape.prototype.draw = function(ctx, width, height) {
      var radius = this.radius;
      var rotation = this.rotation;
      var numSides = this.numSides;
      var x = this.x;
      var y = this.y;
      var size = Math.max(width, height);
  
      // TODO: use this.___ in here instead of local variables.
  
      ctx.fillStyle = 'rgba(255, 255, 255, ' + this.opacity + ')';
      ctx.beginPath();
      for (var i = 0; i < numSides; ++i) {
        var ang = rotation + i * Math.PI * 2 / numSides;
        if (i == 0) {
          ctx.moveTo((x + Math.cos(ang) * radius) * size,
              (y + Math.sin(ang) * radius) * size);
        } else {
          ctx.lineTo((x + Math.cos(ang) * radius) * size,
              (y + Math.sin(ang) * radius) * size);
        }
      }
      ctx.closePath();
      ctx.fill();
    };
  
    function Shapes(canvas, count) {
      this.canvas = canvas;
      this.movingShapes = [];
  
      // Generate some pentagons to start
      for (var i = 0; i < (count || 18); ++i) {
        var moving = new MovingShape(this.random());
        this.movingShapes.push(moving);
      }
    }
  
    Shapes.prototype.begin = function() {
      setInterval(function() {
        this.draw();
      }.bind(this), 1000/24);
    };
  
    Shapes.prototype.draw = function() {
      var context = this.canvas.getContext('2d');
      var width = this.canvas.width;
      var height = this.canvas.height;
  
      context.clearRect(0, 0, width, height);
  
      // Animate and draw the pentagons
      for (var i = 0, len = this.movingShapes.length; i < len; ++i) {
        var p = this.movingShapes[i];
        p.animation.intermediate(p.pentagon);
  
        // Draw the pentagon
        p.pentagon.draw(context, width, height);
  
        if (p.animation.isDone()) {
          // Generate a new animation
          var newPent = this.random(i);
          var duration = 30 + 30*Math.random();
          p.animation = new Animation(p.pentagon.copy(), newPent, duration);
        }
      }
    };
  
    Shapes.prototype.random = function(ignoreIdx) {
      var radius = (0.11 + (Math.pow(Math.random(), 15)+1.0)*0.075)*0.65;
      var opacity = Math.random()*0.32 + 0.04;
      var numSides = 3 + Math.floor(Math.random() * 3);
  
      if ('undefined' === typeof ignoreIdx) {
        return new Shape(Math.random(), Math.random(), radius,
          Math.random()*Math.PI*2, opacity, numSides);
      }
  
      // The new pentagon is dependent on the previous pentagon.
      var last = this.movingShapes[ignoreIdx].pentagon;
      var coords = this._gravityCoords(ignoreIdx, last);
      var rotation = Math.PI*(Math.random()-0.5) + last.rotation;
  
      return new Shape(coords.x, coords.y, radius, rotation, opacity, last.numSides);
    };
  
    Shapes.prototype._gravityCoords = function(ignoreIdx, last) {
      var newCoords = {};
  
      // Use gravity to figure out where the pentagon "wants" to go.
      for (var j = 0; j < 2; ++j) {
        var axis = (j === 0 ? "x" : "y");
        var axisCoord = last[axis];
  
        // Apply inverse square forces from edges.
        var force = 1/Math.pow(axisCoord+0.01, 2) - 1/Math.pow(1.01-axisCoord, 2);
  
        // Apply inverse square forces from other pentagons.
        for (var i = 0, len = this.movingShapes.length; i < len; ++i) {
          if (i === ignoreIdx) {
            continue;
          }
          var p = this.movingShapes[i].pentagon;
          var dSquared = Math.pow(p.x-last.x, 2) + Math.pow(p.y-last.y, 2);
          var forceMag = 1/dSquared;
          var distance = Math.sqrt(dSquared);
          force -= forceMag * (p[axis]-axisCoord) / distance;
        }
  
        // Add a random element to the force.
        force += (Math.random()-0.5) * 20;
  
        // Cap the force at +/- 0.2 and add it to the current coordinate.
        force = Math.max(Math.min(force, 100), -100) / 500;
        newCoords[axis] = Math.max(Math.min(force+axisCoord, 1), 0);
        if (isNaN(newCoords[axis])) {
          newCoords[axis] = Math.random();
        }
      }
  
      return newCoords;
    };
  
    $(function() {
      var canvas = $('#shapes')[0];
      var shapes = new Shapes(canvas);
      shapes.begin();
      var resizeFunc = function() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        shapes.draw();
      };
      $(window).resize(resizeFunc);
      resizeFunc();
  
      setTimeout(function() {
        $('#shapes').css({
          opacity: 1,
          '-ms-transform': 'none',
          '-webkit-transform': 'none',
          transform: 'none'
        });
      }, 10);
    });

})();