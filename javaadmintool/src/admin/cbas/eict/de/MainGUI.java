package admin.cbas.eict.de;

import java.awt.Dimension;
import java.awt.EventQueue;
import java.awt.Toolkit;
import javax.swing.JFrame;
import javax.swing.JTabbedPane;
import java.awt.BorderLayout;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JMenuBar;
import javax.swing.JMenu;
import javax.swing.JMenuItem;
import javax.swing.KeyStroke;
import java.awt.event.KeyEvent;
import java.awt.event.InputEvent;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

public class MainGUI {

	private JFrame frame;
	JPanel panelUsers, panelSlices, panelProjects, panelLog;

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					MainGUI window = new MainGUI();		
					window.frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the application.
	 */
	public MainGUI() {
		initialize();		

	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frame = new JFrame();
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setTitle("C-BAS Admin Tool");

		
		JTabbedPane tabbedPane = new JTabbedPane(JTabbedPane.TOP);
		frame.getContentPane().add(tabbedPane, BorderLayout.CENTER);
		
		panelUsers = new Members();
		tabbedPane.addTab("Members", null, panelUsers, null);
		
		
		panelProjects = new Projects();
		tabbedPane.addTab("Projects", null, panelProjects, null);
		
		panelSlices = new Slices();
		tabbedPane.addTab("Slices", null, panelSlices, null);

//		JPanel panelLog = new JPanel();
//		tabbedPane.addTab("Logs", null, panelLog, null);
		
		JMenuBar menuBar = new JMenuBar();
		frame.setJMenuBar(menuBar);
		
		JMenu mnFile = new JMenu("File");
		menuBar.add(mnFile);
		
		JMenuItem mntmExit = new JMenuItem("Exit");
		mntmExit.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				System.exit(0);
			}
		});
		
		JMenuItem mntmAbout = new JMenuItem("About");
		mntmAbout.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				JOptionPane.showMessageDialog(frame, "<html>Admin tool for <a href=\"http://eict.de/c-bas\">C-BAS</a><br/>Version: beta 1<br/><br/>Developed by <a href=\"http://www.eict.de\">EICT GmbH</>, Berlin", "About", JOptionPane.INFORMATION_MESSAGE);
			}
		});
		mnFile.add(mntmAbout);
		mntmExit.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_X, InputEvent.CTRL_MASK | InputEvent.SHIFT_MASK));
		mnFile.add(mntmExit);
		
		frame.pack();
		Dimension dim = Toolkit.getDefaultToolkit().getScreenSize();
		frame.setLocation(dim.width/2-frame.getSize().width/2, dim.height/2-frame.getSize().height/2);						
	}
	
	public void setVisible(boolean f)
	{
		frame.setVisible(f);
	}

}
