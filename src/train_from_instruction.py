import argparse

from src.instruction_utility import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Reads instructions from "<project>/instructions/". '
                    'The script will follow the instructions to setup a '
                    'training environment, train the model, and allows '
                    'to execute bash commands after finishing.')
    parser.add_argument('--instruction', type=str,
                        default='simple_conv2d.json',
                        help='relative path to instructions from <project>/instructions/')

    args = parser.parse_args()

    instruction_parser = InstructionParser(args.instruction)

    model = instruction_parser.get_model()

    compile_kwargs = {}
    if instruction_parser.get_loss() is not None:
        compile_kwargs["loss"] = instruction_parser.get_loss()
    if instruction_parser.get_optimizer() is not None:
        compile_kwargs["optimizer"] = instruction_parser.get_optimizer()
    if instruction_parser.get_metric() is not None:
        compile_kwargs["metrics"] = [instruction_parser.get_metric()]

    model.compile(**compile_kwargs)

    train_dataset = instruction_parser.get_train_dataset()
    validation_dataset = instruction_parser.get_validation_dataset()

    callbacks = instruction_parser.get_callbacks()

    history = model.fit(train_dataset,
                        validation_data=validation_dataset,
                        callbacks=callbacks,
                        **instruction_parser.get_fit_kwargs())

    instruction_parser.write_metadata()
    instruction_parser.zip_results()

    clean_cmd = instruction_parser.get_cleanup_cmd()
    if clean_cmd != "None":
        os.system(instruction_parser.get_cleanup_cmd())