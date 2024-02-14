/** Name: ALL
 * Section: CSC 331
 * Date: 4/17/2023
 * Purpose: Constructs GUI to accessibility/ gets GUI data/ Fully implements GUI. Performs all final
 * calculations for GUI data
 * */



package com.example.finaltransportation;


import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.DatePicker;
import javafx.scene.control.TextField;
import javafx.scene.control.Button;
import java.util.Objects;

public class GUIController{

    @FXML
    public TextField FinalTimeTextField;

    @FXML
    public TextField WeightLimitTextField;

    @FXML
    private Button CalculateButton;

    @FXML
    private ChoiceBox<String> DayChoiceBox;

    @FXML
    private TextField DistanceTextBox;

    @FXML
    private TextField FinalCostTextBox;

    @FXML
    private ChoiceBox<String> FragHeavChoiceBox;

    @FXML
    private CheckBox InsuranceCheckBox;

    @FXML
    private CheckBox SelfMoveCheckBox;

    @FXML
    private TextField StartTimeTextBox;

    @FXML
    private ChoiceBox<String> VehicleChoiceBox;

    @FXML
    private DatePicker dateInterval;

    //initialize method
    public void initialize() {
        ObservableList<String> daysDropbox = FXCollections.observableArrayList("Half Day", "Full Day");
        DayChoiceBox.setItems(daysDropbox); //adds the items to the drop box
        ObservableList<String> vehicleDropbox = FXCollections.observableArrayList("Van, Base Cost 25","PickUp, Base Cost 25","10ft Truck, Base Cost 50","15ft Truck, Base Cost 75","20ft Truck, Base Cost 100","26ft Truck, Base Cost 125");
        VehicleChoiceBox.setItems(vehicleDropbox);
        ObservableList<String> fragileHeavyDropbox = FXCollections.observableArrayList("None", "Only Fragile Items", "Only Heavy Items", "Both Fragile & Heavy Items");
        FragHeavChoiceBox.setItems(fragileHeavyDropbox);
    }

    @FXML
    private void CalculateButton(ActionEvent event){
        try{

            //all we need to do is add the fragile and heavy costs to the total

            boolean movers, halfOrFullDay;
            double total = 0;
            double miles = Double.parseDouble(DistanceTextBox.getText());

            if (InsuranceCheckBox.isSelected()){ //checks insurance check box to add insurance cost to total
                total += 100;
            }else{
                total += 0;
            }

            if (SelfMoveCheckBox.isSelected()){ //checks selfmove check box to see if workers are needed
                movers = false;
            }else{
                movers = true;
            }
            if (Objects.equals(DayChoiceBox.getValue(), "Half Day")){ //checks for if its a half day or full day of work
                halfOrFullDay = true;
            }else{
                halfOrFullDay = false;
            }

            switch (VehicleChoiceBox.getValue()){ //switch to create objects for what vehicle is selected. displays its weight limit too
                case("Van, Base Cost 25"):        // and adds the vehicle cost to the total
                    Van vehicle = new Van(miles);
                    total += vehicle.getVehicleCosts();
                    WeightLimitTextField.setText("Limit of " + vehicle.getWeight_limit() + "lbs");
                    break;
                case("PickUp, Base Cost 25"):
                    PickUp vehicle2 = new PickUp(miles);
                    total += vehicle2.getVehicleCosts();
                    WeightLimitTextField.setText("Limit of " + vehicle2.getWeight_limit() + "lbs");
                    break;
                case("10ft Truck, Base Cost 50"):
                    Truck10Foot vehicle3 = new Truck10Foot(miles);
                    total += vehicle3.getVehicleCosts();
                    WeightLimitTextField.setText("Limit of " + vehicle3.getWeight_limit() + "lbs");
                    break;
                case("15ft Truck, Base Cost 75"):
                    Truck15Foot vehicle4 = new Truck15Foot(miles);
                    total += vehicle4.getVehicleCosts();
                    WeightLimitTextField.setText("Limit of " + vehicle4.getWeight_limit() + "lbs");
                    break;
                case("20ft Truck, Base Cost 100"):
                    Truck20Foot vehicle5 = new Truck20Foot(miles);
                    total += vehicle5.getVehicleCosts();
                    WeightLimitTextField.setText("Limit of " + vehicle5.getWeight_limit() + "lbs");
                    break;
                case("26ft Truck, Base Cost 125"):
                    Truck26Foot vehicle6 = new Truck26Foot(miles);
                    total += vehicle6.getVehicleCosts();
                    WeightLimitTextField.setText("Limit of " + vehicle6.getWeight_limit() + "lbs");
                    break;
            }
            switch (FragHeavChoiceBox.getValue()){ //checks for special objects and adds it to the total depending on the option selected
                case("None"):                       // also creates an object used for its calculation
                    SpecialObjects s1 = new SpecialObjects(false, false);
                    total += s1.calcHFcosts();
                    break;
                case("Only Fragile Items"):
                    SpecialObjects s2 = new SpecialObjects(true, false);
                    total += s2.calcHFcosts();
                    break;
                case("Only Heavy Items"):
                    SpecialObjects s3 = new SpecialObjects(false, true);
                    total += s3.calcHFcosts();
                    break;
                case("Both Fragile & Heavy Items"):
                    SpecialObjects s4 = new SpecialObjects(true, true);
                    total += s4.calcHFcosts();
                    break;
            }

            Cost partialCost = new Cost(miles, movers, halfOrFullDay); //calculates a partial cost
            total += partialCost.calcStaffCost(); // fully calculates the total cost

            FinalCostTextBox.setText(String.valueOf(total)); //output

        }catch (NumberFormatException ex){
            DistanceTextBox.setText("Enter Distance");
            DistanceTextBox.selectAll();
            DistanceTextBox.requestFocus();
        }
    }


    @FXML
    public void CalculateTimeButton(ActionEvent actionEvent) {
        try{
            boolean halfOrFullDay;
            int militaryTime = Integer.parseInt(StartTimeTextBox.getText());

            if (Objects.equals(DayChoiceBox.getValue(), "Half Day")){ //calculates the half or full day end time based off of this boolean value
                halfOrFullDay = true;
            }else{
                halfOrFullDay = false;
            }

            Time object0 = new Time(militaryTime, halfOrFullDay);
            FinalTimeTextField.setText(String.valueOf(object0.calcEndTime())); //displays estimated endtime


        }catch (NumberFormatException ex) {
            StartTimeTextBox.setText("Enter Military Time");
            StartTimeTextBox.selectAll();
            StartTimeTextBox.requestFocus();
        }
    }
}



