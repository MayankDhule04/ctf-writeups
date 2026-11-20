class Maze
{
   static var root;
   static var q0;
   static var q1;
   static var q2;
   static var q3;
   static var activated;
   static var gateCounts;
   static var gateOpen;
   static var q5;
   static var q4;
   static var gateColors = [10962502,12023854,10394165,4353960,7359647,3508870];
   static var level = 0;
   static var px = 1;
   static var py = 1;
   static var checkpointX = 1;
   static var checkpointY = 1;
   static var won = false;
   static var moveCount = 0;
   static var SIZE = 89;
   static var TOTAL = 7921;
   static var CELL = 16;
   static var HUD = 60;
   static var WIDTH = 760;
   static var HEIGHT = 410;
   static var VIEWH = 350;
   static var camX = 0;
   static var camY = 0;
   static var targetCamX = 0;
   static var targetCamY = 0;
   static var lastMove = 0;
   static var noticeUntil = 0;
   static var noticeText = "";
   static var bumpUntil = 0;
   static var q6 = 1;
   function Maze()
   {
   }
   static function main()
   {
      Maze.root = _root;
      Stage.showMenu = false;
      Maze.q0 = D7.a();
      Maze.q1 = D7.b();
      Maze.q2 = D7.c();
      Maze.q3 = D7.d();
      Maze.root.createEmptyMovieClip("game",1);
      Maze.root.createTextField("titleText",2,18,6,270,22);
      Maze.root.createTextField("gateText",3,285,6,460,22);
      Maze.root.createTextField("subText",4,18,30,727,20);
      Maze.root.createTextField("notice",5,170,65,420,22);
      Maze.root.titleText.selectable = false;
      Maze.root.gateText.selectable = false;
      Maze.root.subText.selectable = false;
      Maze.root.notice.selectable = false;
      Maze.root.titleText.textColor = 9240460;
      Maze.root.gateText.textColor = 13421772;
      Maze.root.subText.textColor = 8947848;
      Maze.root.notice.textColor = 16777215;
      Maze.initLevel();
      Maze.root.onEnterFrame = Maze.tick;
   }
   static function f4()
   {
      Maze.q6 = Maze.q6 * 48271 % 2147483647;
      return Maze.q6;
   }
   static function rnd(n)
   {
      return Maze.f4() % n;
   }
   static function f5(n)
   {
      return "p" + n;
   }
   static function initLevel()
   {
      Maze.f0(Number(Maze.q0[Maze.level]));
      Maze.f1(Maze.level);
      Maze.activated = {};
      Maze.gateCounts = [];
      Maze.gateOpen = [];
      var _loc2_ = 0;
      while(_loc2_ < Maze.q1.length)
      {
         Maze.gateCounts[_loc2_] = 0;
         Maze.gateOpen[_loc2_] = false;
         _loc2_ = _loc2_ + 1;
      }
      Maze.moveCount = 0;
      Maze.g2();
      Maze.checkpointX = Maze.px;
      Maze.checkpointY = Maze.py;
      Maze.camX = 0;
      Maze.camY = 0;
      Maze.g4(true);
      Maze.flash("LEVEL " + (Maze.level + 1) + " // 89x89",1400);
      Maze.draw();
   }
   static function f0(seed)
   {
      Maze.q6 = seed % 2147483647;
      if(Maze.q6 <= 0)
      {
         Maze.q6 = 1;
      }
      Maze.q5 = [];
      var _loc4_ = 0;
      while(_loc4_ < Maze.SIZE)
      {
         var _loc13_ = [];
         var _loc3_ = 0;
         while(_loc3_ < Maze.SIZE)
         {
            _loc13_[_loc3_] = "#";
            _loc3_ = _loc3_ + 1;
         }
         Maze.q5[_loc4_] = _loc13_;
         _loc4_ = _loc4_ + 1;
      }
      Maze.q5[1][1] = " ";
      var _loc14_ = [1];
      var _loc15_ = [1];
      var _loc16_ = [2,-2,0,0];
      var _loc17_ = [0,0,2,-2];
      while(_loc14_.length > 0)
      {
         var _loc18_ = _loc14_.length - 1;
         _loc3_ = Number(_loc14_[_loc18_]);
         _loc4_ = Number(_loc15_[_loc18_]);
         var _loc19_ = [];
         var _loc6_ = 0;
         while(_loc6_ < 4)
         {
            var _loc7_ = _loc3_ + Number(_loc16_[_loc6_]);
            var _loc8_ = _loc4_ + Number(_loc17_[_loc6_]);
            if(_loc7_ >= 1 && (_loc7_ < Maze.SIZE - 1 && (_loc8_ >= 1 && (_loc8_ < Maze.SIZE - 1 && Maze.q5[_loc8_][_loc7_] == "#"))))
            {
               _loc19_.push(_loc6_);
            }
            _loc6_ = _loc6_ + 1;
         }
         if(_loc19_.length > 0)
         {
            _loc6_ = Number(_loc19_[Maze.rnd(_loc19_.length)]);
            var _loc9_ = Number(_loc16_[_loc6_]);
            var _loc10_ = Number(_loc17_[_loc6_]);
            _loc7_ = _loc3_ + _loc9_;
            _loc8_ = _loc4_ + _loc10_;
            Maze.q5[_loc4_ + _loc10_ / 2][_loc3_ + _loc9_ / 2] = " ";
            Maze.q5[_loc8_][_loc7_] = " ";
            _loc14_.push(_loc7_);
            _loc15_.push(_loc8_);
         }
         else
         {
            _loc14_.pop();
            _loc15_.pop();
         }
      }
      var _loc20_ = Maze.SIZE + 1;
      var _loc21_ = (Maze.SIZE - 2) * Maze.SIZE + (Maze.SIZE - 2);
      var _loc22_ = new Array(Maze.TOTAL);
      var _loc5_ = 0;
      while(_loc5_ < Maze.TOTAL)
      {
         _loc22_[_loc5_] = -2;
         _loc5_ = _loc5_ + 1;
      }
      var _loc23_ = [_loc20_];
      var _loc24_ = 0;
      _loc22_[_loc20_] = -1;
      var _loc25_ = [1,-1,0,0];
      var _loc26_ = [0,0,1,-1];
      while(_loc24_ < _loc23_.length)
      {
         var _loc11_ = Number(_loc23_[_loc24_++]);
         _loc3_ = _loc11_ % Maze.SIZE;
         _loc4_ = Math.floor(_loc11_ / Maze.SIZE);
         _loc6_ = 0;
         while(_loc6_ < 4)
         {
            _loc7_ = _loc3_ + Number(_loc25_[_loc6_]);
            _loc8_ = _loc4_ + Number(_loc26_[_loc6_]);
            if(!(_loc7_ < 0 || (_loc7_ >= Maze.SIZE || (_loc8_ < 0 || _loc8_ >= Maze.SIZE))))
            {
               var _loc12_ = _loc8_ * Maze.SIZE + _loc7_;
               if(_loc22_[_loc12_] == -2 && Maze.q5[_loc8_][_loc7_] != "#")
               {
                  _loc22_[_loc12_] = _loc11_;
                  _loc23_.push(_loc12_);
               }
            }
            _loc6_ = _loc6_ + 1;
         }
      }
      var _loc27_ = [];
      var _loc28_ = _loc21_;
      while(_loc28_ != -1 && _loc28_ != -2)
      {
         _loc27_.push(_loc28_);
         _loc28_ = Number(_loc22_[_loc28_]);
      }
      _loc27_.reverse();
      var _loc29_ = {};
      _loc5_ = 0;
      while(_loc5_ < _loc27_.length)
      {
         _loc29_[Maze.f5(Number(_loc27_[_loc5_]))] = true;
         _loc5_ = _loc5_ + 1;
      }
      var _loc30_ = [];
      var _loc31_ = {};
      _loc5_ = 0;
      while(_loc5_ < 6)
      {
         var _loc32_ = Math.round((_loc5_ + 1) * _loc27_.length / 7);
         if(_loc32_ < 2)
         {
            _loc32_ = 2;
         }
         if(_loc32_ > _loc27_.length - 3)
         {
            _loc32_ = _loc27_.length - 3;
         }
         _loc11_ = Number(_loc27_[_loc32_]);
         _loc30_[_loc5_] = _loc11_;
         _loc31_[Maze.f5(_loc11_)] = true;
         _loc3_ = _loc11_ % Maze.SIZE;
         _loc4_ = Math.floor(_loc11_ / Maze.SIZE);
         Maze.q5[_loc4_][_loc3_] = String.fromCharCode(65 + _loc5_);
         _loc5_ = _loc5_ + 1;
      }
      var _loc33_ = new Array(Maze.TOTAL);
      _loc5_ = 0;
      while(_loc5_ < 6)
      {
         var _loc34_ = {};
         var _loc35_ = _loc5_;
         while(_loc35_ < 6)
         {
            _loc34_[Maze.f5(Number(_loc30_[_loc35_]))] = true;
            _loc35_ = _loc35_ + 1;
         }
         var _loc36_ = new Array(Maze.TOTAL);
         _loc23_ = [_loc20_];
         _loc24_ = 0;
         _loc36_[_loc20_] = true;
         while(_loc24_ < _loc23_.length)
         {
            _loc11_ = Number(_loc23_[_loc24_++]);
            _loc3_ = _loc11_ % Maze.SIZE;
            _loc4_ = Math.floor(_loc11_ / Maze.SIZE);
            _loc6_ = 0;
            while(_loc6_ < 4)
            {
               _loc7_ = _loc3_ + Number(_loc25_[_loc6_]);
               _loc8_ = _loc4_ + Number(_loc26_[_loc6_]);
               if(!(_loc7_ < 0 || (_loc7_ >= Maze.SIZE || (_loc8_ < 0 || _loc8_ >= Maze.SIZE))))
               {
                  _loc12_ = _loc8_ * Maze.SIZE + _loc7_;
                  if(Maze.q5[_loc8_][_loc7_] != "#" && (!_loc34_[Maze.f5(_loc12_)] && !_loc36_[_loc12_]))
                  {
                     _loc36_[_loc12_] = true;
                     _loc23_.push(_loc12_);
                  }
               }
               _loc6_ = _loc6_ + 1;
            }
         }
         var _loc37_ = [];
         var _loc38_ = [];
         var _loc39_ = [];
         _loc4_ = 1;
         while(_loc4_ < Maze.SIZE - 1)
         {
            _loc3_ = 1;
            while(_loc3_ < Maze.SIZE - 1)
            {
               _loc11_ = _loc4_ * Maze.SIZE + _loc3_;
               if(!(!_loc36_[_loc11_] || (_loc33_[_loc11_] || (_loc11_ == _loc20_ || (_loc11_ == _loc21_ || _loc31_[Maze.f5(_loc11_)])))))
               {
                  if(!_loc29_[Maze.f5(_loc11_)] && Maze.f6(_loc3_,_loc4_) == 1)
                  {
                     _loc37_.push(_loc11_);
                  }
                  else if(!_loc29_[Maze.f5(_loc11_)])
                  {
                     _loc38_.push(_loc11_);
                  }
                  else
                  {
                     _loc39_.push(_loc11_);
                  }
               }
               _loc3_ += 2;
            }
            _loc4_ += 2;
         }
         var _loc40_ = [_loc37_,_loc38_,_loc39_];
         var _loc41_ = 0;
         var _loc42_ = 0;
         while(_loc42_ < 3 && _loc41_ < Number(Maze.q1[_loc5_]))
         {
            var _loc43_ = _loc40_[_loc42_];
            while(_loc43_.length > 0 && _loc41_ < Number(Maze.q1[_loc5_]))
            {
               var _loc44_ = Maze.rnd(_loc43_.length);
               var _loc45_ = Number(_loc43_[_loc44_]);
               _loc43_.splice(_loc44_,1);
               _loc3_ = _loc45_ % Maze.SIZE;
               _loc4_ = Math.floor(_loc45_ / Maze.SIZE);
               Maze.q5[_loc4_][_loc3_] = String.fromCharCode(97 + _loc5_);
               _loc41_ = _loc41_ + 1;
            }
            _loc42_ = _loc42_ + 1;
         }
         _loc33_ = _loc36_;
         _loc5_ = _loc5_ + 1;
      }
      Maze.q5[1][1] = "S";
      Maze.q5[Maze.SIZE - 2][Maze.SIZE - 2] = "X";
   }
   static function f6(x, y)
   {
      var _loc4_ = 0;
      if(Maze.q5[y][x + 1] != "#")
      {
         _loc4_ = _loc4_ + 1;
      }
      if(Maze.q5[y][x - 1] != "#")
      {
         _loc4_ = _loc4_ + 1;
      }
      if(Maze.q5[y + 1][x] != "#")
      {
         _loc4_ = _loc4_ + 1;
      }
      if(Maze.q5[y - 1][x] != "#")
      {
         _loc4_ = _loc4_ + 1;
      }
      return _loc4_;
   }
   static function f1(which)
   {
      Maze.q4 = [];
      var _loc3_ = Number(Maze.q2[which]) % 2147483647;
      if(_loc3_ <= 0)
      {
         _loc3_ = 1;
      }
      var _loc4_ = Maze.q3[which];
      var _loc5_ = 0;
      while(_loc5_ < _loc4_.length)
      {
         _loc3_ = _loc3_ * 48271 % 2147483647;
         Maze.q4[_loc5_] = Number(_loc4_[_loc5_]) ^ Number(_loc3_ % 65536);
         _loc5_ = _loc5_ + 1;
      }
   }
   static function mapWidth()
   {
      return Maze.SIZE;
   }
   static function mapHeight()
   {
      return Maze.SIZE;
   }
   static function tile(x, y)
   {
      if(y < 0 || (y >= Maze.SIZE || (x < 0 || x >= Maze.SIZE)))
      {
         return "#";
      }
      return String(Maze.q5[y][x]);
   }
   static function g2()
   {
      var _loc2_ = 0;
      while(_loc2_ < Maze.SIZE)
      {
         var _loc3_ = 0;
         while(_loc3_ < Maze.SIZE)
         {
            if(Maze.tile(_loc3_,_loc2_) == "S")
            {
               Maze.px = _loc3_;
               Maze.py = _loc2_;
               return undefined;
            }
            _loc3_ = _loc3_ + 1;
         }
         _loc2_ = _loc2_ + 1;
      }
   }
   static function f8(c)
   {
      return c.charCodeAt(0) - 65;
   }
   static function f9(c)
   {
      var _loc3_ = c.charCodeAt(0);
      return _loc3_ >= 65 && _loc3_ <= 70;
   }
   static function g0(c)
   {
      var _loc3_ = c.charCodeAt(0);
      return _loc3_ >= 97 && _loc3_ <= 102;
   }
   static function g1(c)
   {
      return !!Maze.gateOpen[Maze.f8(c)];
   }
   static function f2(x, y)
   {
      var _loc4_ = y * Maze.SIZE + x;
      var _loc5_ = Math.floor(_loc4_ / 16);
      var _loc6_ = 15 - _loc4_ % 16;
      return (Number(Maze.q4[_loc5_]) >> _loc6_ & 1) == 1;
   }
   static function f3(gray, x, y)
   {
      if(!Maze.f2(x,y))
      {
         return gray << 16 | gray << 8 | gray;
      }
      var _loc5_ = gray + 7;
      if(_loc5_ > 255)
      {
         _loc5_ = 255;
      }
      return _loc5_ << 16 | gray << 8 | gray;
   }
   static function f7(x, y, c)
   {
      var _loc5_ = x + "_" + y;
      if(Maze.activated[_loc5_])
      {
         return undefined;
      }
      Maze.activated[_loc5_] = true;
      var _loc6_ = c.charCodeAt(0) - 97;
      Maze.gateCounts[_loc6_] = Number(Maze.gateCounts[_loc6_]) + 1;
      if(Number(Maze.gateCounts[_loc6_]) >= Number(Maze.q1[_loc6_]))
      {
         Maze.gateOpen[_loc6_] = true;
         Maze.flash("DOOR " + String.fromCharCode(65 + _loc6_) + " UNLOCKED",1400);
      }
      else
      {
         Maze.flash(String.fromCharCode(65 + _loc6_) + ": " + Maze.gateCounts[_loc6_] + " / " + Maze.q1[_loc6_],800);
      }
   }
   static function tick()
   {
      var _loc2_ = getTimer();
      if(!Maze.won && _loc2_ - Maze.lastMove >= 70)
      {
         var _loc3_ = 0;
         var _loc4_ = 0;
         if(Key.isDown(Key.LEFT) || Key.isDown(65))
         {
            _loc3_ = -1;
         }
         else if(Key.isDown(Key.RIGHT) || Key.isDown(68))
         {
            _loc3_ = 1;
         }
         else if(Key.isDown(Key.UP) || Key.isDown(87))
         {
            _loc4_ = -1;
         }
         else if(Key.isDown(Key.DOWN) || Key.isDown(83))
         {
            _loc4_ = 1;
         }
         if(_loc3_ != 0 || _loc4_ != 0)
         {
            Maze.lastMove = _loc2_;
            Maze.move(_loc3_,_loc4_);
         }
      }
      Maze.camX += (Maze.targetCamX - Maze.camX) * 0.24;
      Maze.camY += (Maze.targetCamY - Maze.camY) * 0.24;
      if(Math.abs(Maze.targetCamX - Maze.camX) < 0.1)
      {
         Maze.camX = Maze.targetCamX;
      }
      if(Math.abs(Maze.targetCamY - Maze.camY) < 0.1)
      {
         Maze.camY = Maze.targetCamY;
      }
      Maze.draw();
   }
   static function move(dx, dy)
   {
      if(Maze.won)
      {
         return undefined;
      }
      var _loc4_ = Maze.px + dx;
      var _loc5_ = Maze.py + dy;
      var _loc6_ = Maze.tile(_loc4_,_loc5_);
      if(_loc6_ == "#")
      {
         Maze.px = Maze.checkpointX;
         Maze.py = Maze.checkpointY;
         Maze.bumpUntil = getTimer() + 240;
         Maze.flash("WALL HIT // CHECKPOINT RESTORED",650);
         Maze.g4(false);
         return undefined;
      }
      if(Maze.f9(_loc6_) && !Maze.g1(_loc6_))
      {
         var _loc7_ = Maze.f8(_loc6_);
         Maze.flash("DOOR " + _loc6_ + " LOCKED  " + Maze.gateCounts[_loc7_] + " / " + Maze.q1[_loc7_],800);
         return undefined;
      }
      Maze.px = _loc4_;
      Maze.py = _loc5_;
      Maze.moveCount = Maze.moveCount + 1;
      if(Maze.g0(_loc6_))
      {
         Maze.f7(Maze.px,Maze.py,_loc6_);
      }
      if(Maze.f9(_loc6_) && Maze.g1(_loc6_))
      {
         Maze.checkpointX = Maze.px;
         Maze.checkpointY = Maze.py;
         Maze.flash("CHECKPOINT " + _loc6_,600);
      }
      if(_loc6_ == "X")
      {
         Maze.g3();
      }
      Maze.g4(false);
   }
   static function g3()
   {
      Maze.level = Maze.level + 1;
      if(Maze.level >= Maze.q0.length)
      {
         Maze.won = true;
         return undefined;
      }
      Maze.initLevel();
   }
   static function flash(s, ms)
   {
      Maze.noticeText = s;
      Maze.noticeUntil = getTimer() + ms;
   }
   static function g4(snap)
   {
      var _loc3_ = Maze.SIZE * Maze.CELL;
      var _loc4_ = Maze.SIZE * Maze.CELL;
      Maze.targetCamX = (Maze.px + 0.5) * Maze.CELL - Maze.WIDTH / 2;
      Maze.targetCamY = (Maze.py + 0.5) * Maze.CELL - Maze.VIEWH / 2;
      if(Maze.targetCamX < 0)
      {
         Maze.targetCamX = 0;
      }
      if(Maze.targetCamY < 0)
      {
         Maze.targetCamY = 0;
      }
      if(Maze.targetCamX > _loc3_ - Maze.WIDTH)
      {
         Maze.targetCamX = _loc3_ - Maze.WIDTH;
      }
      if(Maze.targetCamY > _loc4_ - Maze.VIEWH)
      {
         Maze.targetCamY = _loc4_ - Maze.VIEWH;
      }
      if(snap)
      {
         Maze.camX = Maze.targetCamX;
         Maze.camY = Maze.targetCamY;
      }
   }
   static function rect(mc, x, y, w, h, color)
   {
      mc.lineStyle();
      mc.beginFill(color,100);
      mc.moveTo(x,y);
      mc.lineTo(x + w,y);
      mc.lineTo(x + w,y + h);
      mc.lineTo(x,y + h);
      mc.lineTo(x,y);
      mc.endFill();
   }
   static function outline(mc, x, y, w, h, color)
   {
      mc.lineStyle(1,color,100);
      mc.moveTo(x,y);
      mc.lineTo(x + w,y);
      mc.lineTo(x + w,y + h);
      mc.lineTo(x,y + h);
      mc.lineTo(x,y);
   }
   static function marker(mc, x, y, idx, color)
   {
      mc.lineStyle(1,color,100);
      var _loc7_ = 0;
      while(_loc7_ < idx + 1)
      {
         var _loc8_ = x + 3 + _loc7_ * 2;
         mc.moveTo(_loc8_,y + 4);
         mc.lineTo(_loc8_,y + 12);
         _loc7_ = _loc7_ + 1;
      }
   }
   static function g5()
   {
      var _loc2_ = "";
      var _loc3_ = 0;
      while(_loc3_ < Maze.q1.length)
      {
         if(_loc3_ > 0)
         {
            _loc2_ += "  ";
         }
         _loc2_ += String.fromCharCode(65 + _loc3_) + ":" + Maze.gateCounts[_loc3_] + "/" + Maze.q1[_loc3_] + (!Maze.gateOpen[_loc3_] ? "" : "+");
         _loc3_ = _loc3_ + 1;
      }
      return _loc2_;
   }
   static function h7()
   {
      var _loc2_ = [9,38,58,176,236,243,153,145,197,161,70,75,9,116,14,10,40,44,175,244,249,135,243,169,176,85,68,105,126,15,117];
      var _loc3_ = "";
      var _loc4_ = 0;
      while(_loc4_ < _loc2_.length)
      {
         _loc3_ += String.fromCharCode(Number(_loc2_[_loc4_]) ^ _loc4_ * 17 + 93 & 0xFF);
         _loc4_ = _loc4_ + 1;
      }
      return _loc3_;
   }
   static function draw()
   {
      var _loc2_ = Maze.root.game;
      _loc2_.clear();
      Maze.rect(_loc2_,0,0,Maze.WIDTH,Maze.HEIGHT,526344);
      Maze.rect(_loc2_,0,0,Maze.WIDTH,Maze.HUD - 1,1052688);
      Maze.rect(_loc2_,0,Maze.HUD - 1,Maze.WIDTH,1,2434341);
      Maze.root.titleText.text = "FLASHBACK";
      if(Maze.won)
      {
         Maze.root.gateText.text = "ALL 5 LEVELS COMPLETE";
         Maze.root.subText.text = "YOU ESCAPED.";
         Maze.root.notice._x = 160;
         Maze.root.notice._y = 180;
         Maze.root.notice._width = 520;
         Maze.root.notice.text = Maze.h7();
         return undefined;
      }
      Maze.root.notice._x = 170;
      Maze.root.notice._y = 65;
      Maze.root.notice._width = 420;
      Maze.root.gateText.text = Maze.g5();
      Maze.root.subText.text = "LEVEL " + (Maze.level + 1) + "/5   MAP 89x89   MOVES " + Maze.moveCount + "      ARROWS/WASD   wall = checkpoint reset";
      Maze.root.notice.text = getTimer() >= Maze.noticeUntil ? "" : Maze.noticeText;
      var _loc3_ = 0;
      if(getTimer() < Maze.bumpUntil)
      {
         _loc3_ = Math.floor(getTimer() / 35) % 2 != 0 ? 3 : -3;
      }
      var _loc4_ = Math.max(0,Math.floor(Maze.camX / Maze.CELL) - 1);
      var _loc5_ = Math.max(0,Math.floor(Maze.camY / Maze.CELL) - 1);
      var _loc6_ = Math.min(Maze.SIZE - 1,Math.ceil((Maze.camX + Maze.WIDTH) / Maze.CELL) + 1);
      var _loc7_ = Math.min(Maze.SIZE - 1,Math.ceil((Maze.camY + Maze.VIEWH) / Maze.CELL) + 1);
      var _loc8_ = _loc5_;
      while(_loc8_ <= _loc7_)
      {
         var _loc9_ = _loc4_;
         while(_loc9_ <= _loc6_)
         {
            var _loc10_ = Maze.tile(_loc9_,_loc8_);
            var _loc11_ = Math.floor(_loc9_ * Maze.CELL - Maze.camX) + _loc3_;
            var _loc12_ = Math.floor(Maze.HUD + _loc8_ * Maze.CELL - Maze.camY);
            if(_loc10_ == "#")
            {
               Maze.rect(_loc2_,_loc11_,_loc12_,Maze.CELL,Maze.CELL,Maze.f3(23,_loc9_,_loc8_));
               Maze.outline(_loc2_,_loc11_ + 0.5,_loc12_ + 0.5,Maze.CELL - 1,Maze.CELL - 1,2500134);
            }
            else
            {
               var _loc13_ = (_loc9_ + _loc8_) % 2 != 0 ? 12 : 15;
               Maze.rect(_loc2_,_loc11_,_loc12_,Maze.CELL,Maze.CELL,Maze.f3(_loc13_,_loc9_,_loc8_));
               if(_loc10_ == "S")
               {
                  Maze.outline(_loc2_,_loc11_ + 3,_loc12_ + 3,Maze.CELL - 6,Maze.CELL - 6,5076628);
               }
               if(_loc10_ == "X")
               {
                  Maze.rect(_loc2_,_loc11_ + 3,_loc12_ + 3,Maze.CELL - 6,Maze.CELL - 6,3920987);
                  Maze.rect(_loc2_,_loc11_ + 6,_loc12_ + 6,Maze.CELL - 12,Maze.CELL - 12,597006);
               }
               if(Maze.f9(_loc10_))
               {
                  var _loc14_ = Maze.f8(_loc10_);
                  if(!Maze.gateOpen[_loc14_])
                  {
                     Maze.rect(_loc2_,_loc11_ + 2,_loc12_ + 2,Maze.CELL - 4,Maze.CELL - 4,Maze.gateColors[_loc14_]);
                     Maze.marker(_loc2_,_loc11_,_loc12_,_loc14_,16777215);
                  }
                  else
                  {
                     Maze.outline(_loc2_,_loc11_ + 2,_loc12_ + 2,Maze.CELL - 4,Maze.CELL - 4,4165967);
                  }
               }
               if(Maze.g0(_loc10_))
               {
                  var _loc15_ = _loc10_.charCodeAt(0) - 97;
                  var _loc16_ = _loc9_ + "_" + _loc8_;
                  var _loc17_ = !!Maze.activated[_loc16_];
                  var _loc18_ = _loc15_ >= 4 && !_loc17_;
                  if(_loc18_)
                  {
                     Maze.rect(_loc2_,_loc11_ + 7,_loc12_ + 7,2,2,1118481);
                  }
                  else
                  {
                     Maze.rect(_loc2_,_loc11_ + 4,_loc12_ + 4,Maze.CELL - 8,Maze.CELL - 8,!_loc17_ ? Maze.gateColors[_loc15_] : 2586682);
                     Maze.marker(_loc2_,_loc11_,_loc12_,_loc15_,!_loc17_ ? 16777215 : 12124097);
                  }
               }
            }
            _loc9_ = _loc9_ + 1;
         }
         _loc8_ = _loc8_ + 1;
      }
      var _loc19_ = Math.floor(Maze.px * Maze.CELL - Maze.camX) + _loc3_;
      var _loc20_ = Math.floor(Maze.HUD + Maze.py * Maze.CELL - Maze.camY);
      Maze.rect(_loc2_,_loc19_ + 4,_loc20_ + 4,Maze.CELL - 8,Maze.CELL - 8,getTimer() >= Maze.bumpUntil ? 5614335 : 16730698);
      Maze.outline(_loc2_,_loc19_ + 4,_loc20_ + 4,Maze.CELL - 8,Maze.CELL - 8,12180479);
   }
}
