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
  UpdateKeyGroupRequest,
  UpdateKeyGroupResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateKeyGroupCommandInput extends UpdateKeyGroupRequest {}
export interface UpdateKeyGroupCommandOutput
  extends UpdateKeyGroupResult,
    __MetadataBearer {}
export declare class UpdateKeyGroupCommand extends $Command<
  UpdateKeyGroupCommandInput,
  UpdateKeyGroupCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateKeyGroupCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateKeyGroupCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<UpdateKeyGroupCommandInput, UpdateKeyGroupCommandOutput>;
  private serialize;
  private deserialize;
}
