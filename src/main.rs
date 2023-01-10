mod simple_logger;
use simple_logger::Logger;

use dotenv::dotenv;
use std::env;

fn main() {
    // Load our enviroment
    dotenv().ok();

    println!("{}", env::var("DISCORD_TOKEN").unwrap());



    let logger = Logger::new(false);


    logger.info("testing...");
}
