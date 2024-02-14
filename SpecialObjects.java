/** Name: Blaise
 * Section: CSC 331
 * Date: 4/17/2023
 * Purpose: Creates Special Objects/ assigns their costs
 * */

package com.example.finaltransportation;

public class SpecialObjects{
    //instance variables
    private boolean fragile;
    private final int Fragilefee = 20;
    private final int heavyfee = 50;
    private boolean heavy;

    //constructor
    public SpecialObjects(boolean fragile, boolean heavy){
        this.fragile = fragile;
        this.heavy = heavy;
    }
    //accessors
    public boolean getFragile() { return fragile;}
    public boolean getHeavy() {return heavy;}


    //mutators
    public void setFragile(boolean fragile) {this.fragile = fragile;}
    public void setHeavy(boolean heavy) {this.heavy = heavy;}

    //other methods
    public int calcHFcosts(){ //determines what cost is added to the total based on input from GUI
        if (fragile & heavy) {
            return 75;
        } else if (fragile == true & heavy ==false) {
            return 20;
        } else if (fragile == false & heavy) {
            return 50;
        }else
        return 0;
    }
}

//SpecialObjects[] options = new SpecialObjects[4]
//options[0] = new SpecialObjects(false, false, 0);  //no special objects
//options[1] = new SpecialObjects(true, false, 20); //only fragile objects
//options[2] = new SpecialObjects(true, true, 75);  //both fragile and heavy objects
//options[3] = new SpecialObjects(false, true, 50);  //only heavy objects
