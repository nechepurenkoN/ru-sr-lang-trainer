use teloxide::{dispatching::dialogue::InMemStorage, filter_command, prelude::*, utils::command::BotCommands};

type AppDialogue = Dialogue<State, InMemStorage<State>>;
type HandlerResult = Result<(), Box<dyn std::error::Error + Send + Sync>>;

#[derive(Clone, Default)]
pub enum State {
    #[default]
    Start,
    Exercise {
        exercise_id: String,
    },
}

#[derive(Clone, BotCommands)]
#[command(rename_rule = "lowercase", description = "These commands are supported:")]
pub enum Command {
    #[command(description = "Choose exercise by id.")]
    Exercise { id: String },
    #[command(description = "Help")]
    Help,
}

#[derive(Clone, BotCommands)]
#[command(rename_rule = "lowercase", description = "These exercise commands are supported:")]
pub enum ExerciseCommand {
    Task { id: String },
    Theory,
    Exit,
}

#[tokio::main]
async fn main() {
    pretty_env_logger::init();
    log::info!("Starting throw dice bot...");

    let bot = Bot::from_env();

    Dispatcher::builder(
        bot,
        Update::filter_message()
            .enter_dialogue::<Message, InMemStorage<State>, State>()
            .branch(dptree::case![State::Start]
                .branch(dptree::entry().filter_command::<Command>().endpoint(start_received_command))
                .branch(dptree::endpoint(help))
            )
            .branch(dptree::case![State::Exercise { exercise_id }]
                .branch(dptree::entry().filter_command::<ExerciseCommand>().endpoint(exercise_received_command))
                .branch(dptree::endpoint(exercise_help))
            ),
    )
        .dependencies(dptree::deps![InMemStorage::<State>::new()])
        .enable_ctrlc_handler()
        .build()
        .dispatch()
        .await;
}

async fn help(bot: Bot, dialogue: AppDialogue, msg: Message) -> HandlerResult {
    bot.send_message(msg.chat.id, "Help message").await?;
    dialogue.update(State::Start).await?;
    Ok(())
}

async fn start_received_command(_bot: Bot, dialogue: AppDialogue, _msg: Message, cmd: Command) -> HandlerResult {
    match cmd {
        Command::Exercise { id } => {
            dialogue.update(State::Exercise { exercise_id: id }).await?;
        }
        Command::Help => {
            dialogue.update(State::Start).await?;
        }
    }

    Ok(())
}

async fn exercise_help(bot: Bot, _dialogue: AppDialogue, msg: Message) -> HandlerResult {
    bot.send_message(msg.chat.id, "Exercise help message").await?;
    Ok(())
}

async fn exercise_received_command(bot: Bot, dialogue: AppDialogue, exercise_id: String, msg: Message, cmd: ExerciseCommand) -> HandlerResult {
    match cmd {
        ExerciseCommand::Task { id } => {
            bot.send_message(msg.chat.id, format!("Ex id: {}, task id: {}", exercise_id, id)).await?;
        }
        ExerciseCommand::Theory => {
            bot.send_message(msg.chat.id, format!("Theory requested for exercise: {}", exercise_id)).await?;
        }
        ExerciseCommand::Exit => {
            dialogue.update(State::Start).await?;
        }
    }

    Ok(())
}