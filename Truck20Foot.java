/** Name: CJ
 * Section: CSC 331
 * Date: 4/17/2023
 * Purpose: Creates Truck20Foot Option for GUI/ calculates vehicle cost
 * */

package com.example.finaltransportation;

//subclass
public class Truck20Foot extends Cost{
    private double miles;
    private final double mpg = 10, gasCost = 3.5;


    public Truck20Foot(double miles){
        this.miles = miles;
    }

    //getters
    public int getWeight_limit(){
        return 6385;}
    public double getGasCost(){return gasCost;}

    public double getVehicleCosts(){
        return (miles/mpg)*gasCost+ 100;//25 is the base cost for the van
    }
}