package admin.cbas.eict.de;

import org.jdesktop.swingx.calendar.SingleDaySelectionModel;
import org.jdesktop.swingx.JXDatePicker;

import javax.swing.*;
import javax.swing.text.DefaultFormatterFactory;
import javax.swing.text.DateFormatter;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;
import java.awt.*;

/**
 * This is licensed under LGPL.  License can be found here:  http://www.gnu.org/licenses/lgpl-3.0.txt
 *
 * This is provided as is.  If you have questions please direct them to charlie.hubbard at gmail dot you know what.
 */
public class DateTimePicker extends JXDatePicker {
    /**
	 * 
	 */
	private static final long serialVersionUID = 1068132004796943387L;
	private JSpinner timeSpinner;
    private JPanel timePanel;
    private DateFormat timeFormat;

    public DateTimePicker() {
        super();
        getMonthView().setSelectionModel(new SingleDaySelectionModel());
    }

    public DateTimePicker( Date d ) {
        this();
        setDate(d);
    }

    public void commitEdit() throws ParseException {
        commitTime();
        super.commitEdit();
    }

    public void cancelEdit() {
        super.cancelEdit();
        setTimeSpinners();
    }

    @Override
    public JPanel getLinkPanel() {
        super.getLinkPanel();
        if( timePanel == null ) {
            timePanel = createTimePanel();
        }
        setTimeSpinners();
        return timePanel;
    }

    private JPanel createTimePanel() {
        JPanel newPanel = new JPanel();
        newPanel.setLayout(new FlowLayout());
        //newPanel.add(panelOriginal);

        SpinnerDateModel dateModel = new SpinnerDateModel();
        timeSpinner = new JSpinner(dateModel);        
        ((JSpinner.DateEditor) timeSpinner.getEditor()).getFormat().applyPattern("HH:mm:ss");
        //((JSpinner.DefaultEditor) timeSpinner.getEditor()).getTextField().setEditable(false);
        if( timeFormat == null ) timeFormat = new SimpleDateFormat("HH:mm:ss");        
        JFormattedTextField tf = ((JSpinner.DefaultEditor) timeSpinner.getEditor()).getTextField();
        tf.setText(timeFormat.format(new Date()));
        updateTextFieldFormat();
        newPanel.add(new JLabel( "Time:" ) );
        newPanel.add(timeSpinner);
        newPanel.setBackground(Color.WHITE);
        return newPanel;
    }

    private void updateTextFieldFormat() {
        if( timeSpinner == null ) return;
        JFormattedTextField tf = ((JSpinner.DefaultEditor) timeSpinner.getEditor()).getTextField();
        DefaultFormatterFactory factory = (DefaultFormatterFactory) tf.getFormatterFactory();
        DateFormatter formatter = (DateFormatter) factory.getDefaultFormatter();
        // Change the date format to only show the hours
        formatter.setFormat( timeFormat );
    }

    private void commitTime() {
        Date date = getDate();
        if (date != null) {
            Date time = (Date) timeSpinner.getValue();
            GregorianCalendar timeCalendar = new GregorianCalendar();
            timeCalendar.setTime( time );

            GregorianCalendar calendar = new GregorianCalendar();
            calendar.setTime(date);
            calendar.set(Calendar.HOUR_OF_DAY, timeCalendar.get( Calendar.HOUR_OF_DAY ) );
            calendar.set(Calendar.MINUTE, timeCalendar.get( Calendar.MINUTE ) );
            calendar.set(Calendar.SECOND, 0);
            calendar.set(Calendar.MILLISECOND, 0);

            Date newDate = calendar.getTime();
            setDate(newDate);
        }

    }

    private void setTimeSpinners() {    	
        Date date = getDate();
        if (date != null) {
            timeSpinner.setValue( date );
        }
    }

    public DateFormat getTimeFormat() {
        return timeFormat;
    }

    public void setTimeFormat(DateFormat timeFormat) {
        this.timeFormat = timeFormat;
        updateTextFieldFormat();
    }

}
