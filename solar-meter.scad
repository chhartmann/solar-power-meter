usbWidth = 9.5;
usbHeight = 3.8;

$fn=50;

include <../YAPPgenerator_v3.scad>

//-- which part(s) do you want to print?
printBaseShell        = true;
printLidShell         = true;
printSwitchExtenders  = false;
shiftLid              = 0;  // Set the distance between the lid and base when rendered or previewed side by side
                            
//-- padding between pcb and inside wall
paddingFront        = 1;
paddingBack         = 1;
paddingRight        = 0.5;
paddingLeft         = 0.5;

// ********************************************************************
// The Following will be used as the first element in the pbc array

//Defined here so you can define the "Main" PCB using these if wanted
pcbLength           = 85; // Front to back
pcbWidth            = 18; // Side to side
pcbThickness        = 1.0;
standoffHeight      = 0.0;  //-- How much the PCB needs to be raised from the base to leave room for solderings 
standoffDiameter    = 3;
standoffPinDiameter = 0;
standoffHoleSlack   = 0.0;



wallThickness       = 1.8;
basePlaneThickness  = 1.2;
lidPlaneThickness   = 1.2;

//-- Total height of box = lidPlaneThickness 
//                       + lidWallHeight 
//--                     + baseWallHeight 
//                       + basePlaneThickness
//-- space between pcb and lidPlane :=
//--      (bottonWallHeight+lidWallHeight) - (standoffHeight+pcbThickness)
baseWallHeight      = 5;
lidWallHeight       = 2;

//-- ridge where base and lid off box can overlap
//-- Make sure this isn't less than lidWallHeight
ridgeHeight         = 4.0;
ridgeSlack          = 0.4;
roundRadius         = 1.5;

//---------------------------
//--     C O N T R O L     --
//---------------------------
// -- Render --
renderQuality             = 8;          //-> from 1 to 32, Default = 8

// --Preview --
previewQuality            = 5;          //-> from 1 to 32, Default = 5
showSideBySide            = true;       //-> Default = true
onLidGap                  = 0;  // tip don't override to animate the lid opening
//onLidGap                  = ((ridgeHeight) - (ridgeHeight * abs(($t-0.5)*2)))*2;  // tip don't override to animate the lid opening/closing
colorLid                  = "YellowGreen";   
alphaLid                  = 1;
colorBase                 = "BurlyWood";
alphaBase                 = 1;
hideLidWalls              = false;      //-> Remove the walls from the lid : only if preview and showSideBySide=true 
hideBaseWalls             = false;      //-> Remove the walls from the base : only if preview and showSideBySide=true  
showOrientation           = true;       //-> Show the Front/Back/Left/Right labels : only in preview
showPCB                   = false;      //-> Show the PCB in red : only in preview 
showSwitches              = false;      //-> Show the switches (for pushbuttons) : only in preview 
showButtonsDepressed      = false;      //-> Should the buttons in the Lid On view be in the pressed position
showOriginCoordBox        = false;      //-> Shows red bars representing the origin for yappCoordBox : only in preview 
showOriginCoordBoxInside  = false;      //-> Shows blue bars representing the origin for yappCoordBoxInside : only in preview 
showOriginCoordPCB        = false;      //-> Shows blue bars representing the origin for yappCoordBoxInside : only in preview 
showMarkersPCB            = false;      //-> Shows black bars corners of the PCB : only in preview 
showMarkersCenter         = true;      //-> Shows magenta bars along the centers of all faces  
inspectX                  = 0;          //-> 0=none (>0 from Back)
inspectY                  = 0;          //-> 0=none (>0 from Right)
inspectZ                  = 0;          //-> 0=none (>0 from Bottom)
inspectXfromBack          = true;       //-> View from the inspection cut foreward
inspectYfromLeft          = true;       //-> View from the inspection cut to the right
inspectZfromBottom        = true;       //-> View from the inspection cut up
//---------------------------
//--     C O N T R O L     --
//---------------------------



// USB
cutoutsFront = 
[
   [(pcbWidth/2) - (usbWidth/2), 
     0, 
     usbWidth,
     usbHeight, 
     0, yappRectangle],
];  

// Button
translate([wallThickness + pcbLength + 2 -8.5, 3*wallThickness + pcbWidth + 1.5 + 10 + 7, wallThickness-0.5])
cylinder(h=4, r=1.5);

// LEDs + Button
cutoutsLid =  
[
   [35.5, pcbWidth/2, 69, 5, 5, yappRectangle, yappCenter],

   [80.2, 9, 9, .6, 5, yappRectangle, yappCenter],
   [80.2, 13.0, 9, .6, 5, yappRectangle, yappCenter],
   [75.7, 11.0, .6, 4.6, 5, yappRectangle, yappCenter],
   
];


pcbStands = [
  [pcbLength - 20, pcbWidth-1, yappLidOnly, yappPin],
  [pcbLength - 20, 1, yappLidOnly, yappPin],
  [pcbLength-8, pcbWidth-1, yappLidOnly, yappPin],
  [pcbLength-8, 1, yappLidOnly, yappPin],
];

snapJoins   =   
[
   [(shellLength/2)-25,     5, yappLeft, yappRight, yappCenter, yappSymmetric]
];


// PCB end stop

translate([wallThickness + pcbLength - 3 - 23,wallThickness, wallThickness-0.5])
cube([5,5,4], center=false);


translate([wallThickness + pcbLength - 3 - 23,pcbWidth-2.5+0.5, wallThickness-0.5])
cube([5,5,4], center=false);



YAPPgenerate();
