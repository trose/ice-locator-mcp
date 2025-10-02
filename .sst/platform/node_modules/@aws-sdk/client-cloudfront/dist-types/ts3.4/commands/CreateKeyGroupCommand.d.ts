import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  CreateKeyGroupRequest,
  CreateKeyGroupResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateKeyGroupCommandInput extends CreateKeyGroupRequest {}
export interface CreateKeyGroupCommandOutput
  extends CreateKeyGroupResult,
    __MetadataBearer {}
export declare class CreateKeyGroupCommand extends $Command<
  CreateKeyGroupCommandInput,
  CreateKeyGroupCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateKeyGroupCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateKeyGroupCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<CreateKeyGroupCommandInput, CreateKeyGroupCommandOutput>;
  private serialize;
  private deserialize;
}
