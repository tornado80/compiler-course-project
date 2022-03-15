PROGRAM compilerProjTest;
var
a_var, b_var,c_var,i , chosenOp: integer;
s : real;




procedure findMin(x, y, z: integer; var m: integer);

begin
   if x < y then
      m:= x
   else
      m:= y;

   if z < m then
      m:= z;
end;

begin


    if (a_var <= 0 or a_var <> b_var) then
        a_var := 2;
    else
        s := (4 / 3) * a_var * a_var * a_var * (7 div 2);


    while b_var > 10 do
    begin
       findMin(a_var,b_var,c_var, s);
       b_var := b_var - 2;
       c_var := not c_var;
    end;

    s := s mod 5;
    if(s > 2 and s <4 ) then
        a_var := -005;

end
