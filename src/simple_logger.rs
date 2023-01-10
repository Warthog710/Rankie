use chrono::{Datelike, Local};
use std::fs::OpenOptions;
use std::io::Write;
use std::fs;

pub struct Logger 
{
    stdout: bool
}

impl Logger 
{
    pub fn new(stdout: bool) -> Logger
    {
        Logger{stdout: stdout}
    }

    fn write(&self, level: &str, message: &str)
    {
        let now = Local::now();
        let year = now.year();
        let month = now.month();
        let day = now.day();

        let path = format!("Logs/{}/{}", year, month);
        let file_path = format!("{}/log_{}.log", path, day);

        // Create the log directory if it doesn't already exist
        fs::create_dir_all(path).unwrap();

        let msg = format!("{}/{}/{} @{} - {} | {}\n", year, month, day, now.format("%H:%M:%S"), level, message);

        // Print to stdout if we were asked to do so...
        if self.stdout
        {
            println!("{}", msg);
        }

        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .write(true)
            .open(file_path)
            .unwrap();

        file.write_all(msg.as_bytes()).unwrap();
    }

    pub fn info (&self, message: &str)
    {
        self.write("INFO", message);
    }

    pub fn debug (&self, message: &str)
    {
        self.write("DEBUG", message);
    }

    pub fn warning (&self, message: &str)
    {
        self.write("WARNING", message);
    }

    pub fn error (&self, message: &str)
    {
        self.write("ERROR", message);
    }
}