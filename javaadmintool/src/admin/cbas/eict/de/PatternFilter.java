package admin.cbas.eict.de;

import java.awt.Toolkit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.swing.text.AttributeSet;
import javax.swing.text.BadLocationException;
import javax.swing.text.DocumentFilter;

public class PatternFilter extends DocumentFilter {

    // The pattern must contain all subpatterns so we can enter characters into a text component !
    private Pattern pattern;

    public PatternFilter(String pat) {
        pattern = Pattern.compile(pat);
        System.out.println(pattern);
    }

    public void insertString(FilterBypass fb, int offset, String string, AttributeSet attr)
            throws BadLocationException {

        String newStr = fb.getDocument().getText(0, fb.getDocument().getLength()) + string;
        Matcher m = pattern.matcher(newStr);
        if (m.matches()) {
            super.insertString(fb, offset, string, attr);
        } 
        else
        	Toolkit.getDefaultToolkit().beep();
    }

    public void replace(FilterBypass fb, int offset,
                        int length, String string, AttributeSet attr) throws
            BadLocationException {

        if (length > 0) fb.remove(offset, length);
        insertString(fb, offset, string, attr);
    }
}