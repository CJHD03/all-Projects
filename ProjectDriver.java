/** Name: All
 * Section: CSC 331
 * Date: 4/17/ 2023
 * Purpose: Open /Run the GUI
 * */


package com.example.finaltransportation;

import javafx.application.Application;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.stage.Stage;
import java.io.IOException;
import javafx.scene.control.ChoiceBox;


public class ProjectDriver extends Application {
    @Override
    public void start(Stage stage) throws IOException {
        FXMLLoader fxmlLoader = new FXMLLoader(ProjectDriver.class.getResource("GroupProjectGUI.fxml"));
        Scene scene = new Scene(fxmlLoader.load(), 600, 600);
        stage.setTitle("Transportation CO!!!!!!!!!!!!!!!!!!");
        stage.setScene(scene);
        stage.show();
    }


    public static void main(String[] args) {
        launch();
    }
}